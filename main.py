# [START imports]
import endpoints
from google.appengine.api import search
from google.appengine.ext import ndb
from protorpc import message_types
from protorpc import messages
from protorpc import remote
# [END imports]

INDEX_NAME = 'reportsearch'
REPORT_ID = 'report_id'
LOCATION = 'location'

# [START messages]
class SendReportRequest(messages.Message):
    latitude = messages.FloatField(1)
    longitude = messages.FloatField(2)


class SendReportResponse(messages.Message):
    report_id = messages.StringField(1)
    
   
class RoadkillReportResponse(messages.Message):
    latitude = messages.FloatField(1)
    longitude = messages.FloatField(2)
    timestamp = messages.StringField(3)
    report_id = messages.StringField(4)
    
class GetRadiusReportsRequest(messages.Message):
    latitude = messages.FloatField(1)
    longitude = messages.FloatField(2)
    radius = messages.IntegerField(3)
    limit = messages.IntegerField(4)

class GetRadiusReportsResponse(messages.Message):
    reports = messages.MessageField(RoadkillReportResponse, 1, repeated=True)
    
ROADKILL_RESOURCE = endpoints.ResourceContainer(
    message_types.VoidMessage,
    report_id=messages.StringField(2))
# [END messages]

class RoadkillReport(ndb.Model):
    latitude=ndb.FloatProperty()
    longitude=ndb.FloatProperty()
    timestamp=ndb.DateTimeProperty(auto_now_add=True)


# [START roadkill_api]
@endpoints.api(name='roadkill', version='v1')
class RoadkillApi(remote.Service):

    @endpoints.method(
        SendReportRequest,
        SendReportResponse,
        path='roadkill',
        http_method='POST',
        name='report_roadkill')
    def report_roadkill(self, request):
        report = RoadkillReport(latitude=request.latitude, longitude=request.longitude)
        report_id = report.put().urlsafe()
        
        geopoint = search.GeoPoint(request.latitude, request.longitude)
        index_fields = [
          search.AtomField(name=REPORT_ID, value=report_id),
          search.GeoField(name=LOCATION, value=geopoint)
        ]
        doc = search.Document(doc_id=report_id, fields=index_fields)
        search.Index(name=INDEX_NAME).put(doc)
        
        return SendReportResponse(report_id=report_id)

    @endpoints.method(
        ROADKILL_RESOURCE,
        RoadkillReportResponse,
        path='roadkill/{report_id}',
        http_method='GET',
        name='roadkill')
    def get_roadkill_report(self, request):
        report_key = ndb.Key(urlsafe=request.report_id)
        report = report_key.get()
        resp = RoadkillReportResponse(latitude=report.latitude, longitude=report.longitude, timestamp=str(report.timestamp))
        return resp
        
    @endpoints.method(
        GetRadiusReportsRequest,
        GetRadiusReportsResponse,
        path='roadkill/radius',
        http_method='GET',
        name='roadkill_radius'
    )
    def get_roadkill_in_radius(self, request):
      reports = []
      query = "distance({}, geopoint({},{})) < {}".format(LOCATION, request.latitude, request.longitude, request.radius)
      results = search.Index(INDEX_NAME).search(query)
      for doc in results:
        report_id = doc.doc_id
        report_key = ndb.Key(urlsafe=report_id)
        ndb_report = report_key.get()
        report = RoadkillReportResponse(latitude=ndb_report.latitude, longitude=ndb_report.longitude, timestamp=str(ndb_report.timestamp))
        reports.append(report)
      resp = GetRadiusReportsResponse(reports=reports)
      return resp
# [END roadkill_api]


# [START api_server]
api = endpoints.api_server([RoadkillApi])
# [END api_server]
