# [START imports]
import models
from report_manager import ReportManager
from control_group_manager import ControlGroupManager

import endpoints
from google.appengine.api import search
from google.appengine.ext import ndb
from google.appengine.ext.ndb import msgprop
from protorpc import message_types
from protorpc import messages
from protorpc import remote
# [END imports]

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
      self.roadkill_report_manager = ReportManager()
      self.group_manager = ControlGroupManager()

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
      return self.roadkill_report_manager.update_report(request, request.report_id)
      
    @endpoints.method(
        models.CreateControlGroupRequest,
        models.CreateControlGroupResponse,
        path='control_group',
        http_method='POST',
        name='create_control_group'
    )
    def create_control_group(self, request):
      return self.group_manager.create_group(request)
      
    @endpoints.method(
        models.GetNearbyGroupsRequest,
        models.GetNearbyGroupsResponse,
        path='control_group',
        http_method='GET',
        name='nearby_control_groups'
    )
    def get_nearby_groups(self, request):
      return self.group_manager.get_nearby_groups(request)
# [END roadkill_api]


# [START api_server]
api = endpoints.api_server([RoadkillApi])
# [END api_server]
