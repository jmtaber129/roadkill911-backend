# [START imports]
import endpoints
from google.appengine.ext import ndb
from protorpc import message_types
from protorpc import messages
from protorpc import remote
# [END imports]


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
# [END roadkill_api]


# [START api_server]
api = endpoints.api_server([RoadkillApi])
# [END api_server]
