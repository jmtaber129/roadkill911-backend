# [START imports]
import models
import report_manager

import endpoints
from google.appengine.api import search
from google.appengine.ext import ndb
from google.appengine.ext.ndb import msgprop
from protorpc import message_types
from protorpc import messages
from protorpc import remote
# [END imports]

REPORT_INDEX_NAME = 'reportsearch'
REPORT_ID = 'report_id'
LOCATION = 'location'
GROUP_INDEX_NAME = 'groupsearch'
GROUP_ID = 'group_id'
RADIUS = 'radius'

METERS_PER_MILE = 1609.34

ROADKILL_RESOURCE = endpoints.ResourceContainer(
    message_types.VoidMessage,
    report_id=messages.StringField(2))
    
UPDATE_RESOURCE = endpoints.ResourceContainer(
    models.SendReportRequest,
    report_id=messages.StringField(2))

# [START roadkill_api]
@endpoints.api(name='roadkill', version='v1')
class RoadkillApi(remote.Service):
    def __init__(self):
      self.roadkill_report_manager = report_manager.ReportManager()

    @endpoints.method(
        models.SendReportRequest,
        models.SendReportResponse,
        path='roadkill',
        http_method='POST',
        name='report_roadkill')
    def report_roadkill(self, request):
        return self.roadkill_report_manager.create_report(request)

    @endpoints.method(
        ROADKILL_RESOURCE,
        models.RoadkillReportResponse,
        path='roadkill/{report_id}',
        http_method='GET',
        name='roadkill')
    def get_roadkill_report(self, request):
        return self.roadkill_report_manager.get_report(request.report_id)
        
    @endpoints.method(
        models.GetRadiusReportsRequest,
        models.GetRadiusReportsResponse,
        path='roadkill/radius',
        http_method='GET',
        name='roadkill_radius'
    )
    def get_roadkill_in_radius(self, request):
      return self.roadkill_report_manager.get_report_in_radius(request)
      
    @endpoints.method(
        UPDATE_RESOURCE,
        models.SendReportResponse,
        path='roadkill/{report_id}',
        http_method='PUT',
        name='update_roadkill'
    )
    def update_roadkill_report(self, request):
      return self.roadkill_report_manager.update_report(request)
      
    @endpoints.method(
        models.CreateControlGroupRequest,
        models.CreateControlGroupResponse,
        path='control_group',
        http_method='POST',
        name='create_control_group'
    )
    def create_control_group(self, request):
      group = ControlGroup(name=request.name, email=request.email, latitude=request.latitude, longitude=request.longitude, radius=request.radius*METERS_PER_MILE)
      group_id = group.put().urlsafe()
      
      geopoint = search.GeoPoint(request.latitude, request.longitude)
      index_fields = [
        search.AtomField(name=GROUP_ID, value=group_id),
        search.GeoField(name=LOCATION, value=geopoint),
        search.NumberField(name=RADIUS, value=request.radius*METERS_PER_MILE)
      ]
      doc = search.Document(doc_id=group_id, fields=index_fields)
      search.Index(name=GROUP_INDEX_NAME).put(doc)
      
      return models.CreateControlGroupResponse(group_id=group_id)
      
    @endpoints.method(
        models.GetNearbyGroupsRequest,
        models.GetNearbyGroupsResponse,
        path='control_group',
        http_method='GET',
        name='nearby_control_groups'
    )
    def get_nearby_groups(self, request):
      groups = []
      query_string = 'distance({}, geopoint({},{})) < 10000000'.format(LOCATION, request.latitude, request.longitude)
      radius_expression = search.FieldExpression(name='dist', expression='distance({}, geopoint({},{})) - radius'.format(LOCATION, request.latitude, request.longitude))
      query_options = search.QueryOptions(returned_expressions=[radius_expression])
      query = search.Query(query_string=query_string, options=query_options)
      results = search.Index(GROUP_INDEX_NAME).search(query)
      
      for doc in results:
        if doc.expressions[0].value > 0:
          # Input location outside of group's radius.
          continue;
        group_id = doc.doc_id
        group_key = ndb.Key(urlsafe=group_id)
        ndb_group = group_key.get()
        group = models.CreateControlGroupRequest(email=ndb_group.email, name=ndb_group.name, latitude=ndb_group.latitude, longitude=ndb_group.longitude, radius=ndb_group.radius / METERS_PER_MILE)
        groups.append(group)
      resp = models.GetNearbyGroupsResponse(groups=groups)
      return resp
# [END roadkill_api]


# [START api_server]
api = endpoints.api_server([RoadkillApi])
# [END api_server]
