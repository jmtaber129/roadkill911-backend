from google.appengine.ext import ndb
from google.appengine.ext.ndb import msgprop
from protorpc import message_types
from protorpc import messages

# Proto messages.
class ReportStatus(messages.Enum):
    OPEN = 0
    IN_PROGRESS = 1
    CLOSED = 2
    
class SendReportRequest(messages.Message):
    latitude = messages.FloatField(1)
    longitude = messages.FloatField(2)
    status = messages.EnumField(ReportStatus, 3)

class SendReportResponse(messages.Message):
    report_id = messages.StringField(1)
    
class RoadkillReportResponse(messages.Message):
    latitude = messages.FloatField(1)
    longitude = messages.FloatField(2)
    timestamp = messages.StringField(3)
    status = messages.EnumField(ReportStatus, 4)
    report_id = messages.StringField(5)
    
class GetRadiusReportsRequest(messages.Message):
    latitude = messages.FloatField(1)
    longitude = messages.FloatField(2)
    radius = messages.IntegerField(3)
    limit = messages.IntegerField(4)

class GetRadiusReportsResponse(messages.Message):
    reports = messages.MessageField(RoadkillReportResponse, 1, repeated=True)
    
class CreateControlGroupRequest(messages.Message):
    name = messages.StringField(1)
    email = messages.StringField(2)
    latitude = messages.FloatField(3)
    longitude = messages.FloatField(4)
    radius = messages.FloatField(5)
    
class CreateControlGroupResponse(messages.Message):
    group_id = messages.StringField(1)
    
class GetNearbyGroupsRequest(messages.Message):
    latitude = messages.FloatField(1)
    longitude = messages.FloatField(2)
        
class GetNearbyGroupsResponse(messages.Message):
    groups = messages.MessageField(CreateControlGroupRequest, 1, repeated=True)

# NDB models.
class RoadkillReport(ndb.Model):
    latitude=ndb.FloatProperty()
    longitude=ndb.FloatProperty()
    timestamp=ndb.DateTimeProperty(auto_now_add=True)
    status=msgprop.EnumProperty(ReportStatus)
    
class ControlGroup(ndb.Model):
    name=ndb.StringProperty()
    email=ndb.StringProperty()
    latitude=ndb.FloatProperty()
    longitude=ndb.FloatProperty()
    radius=ndb.FloatProperty()

