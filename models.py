from google.appengine.ext import ndb
from google.appengine.ext.ndb import msgprop
from protorpc import message_types
from protorpc import messages

# Location constants
LOCATION = 'location'
RADIUS = 'radius'
METERS_PER_MILE = 1609.34

# Proto messages.
class ReportStatus(messages.Enum):
  OPEN = 0
  IN_PROGRESS = 1
  CLOSED = 2

class ReportType(messages.Enum):
  DEAD = 0
  INJURED = 1
  STRAY = 2

class AnimalDescription(messages.Message):
  size = messages.StringField(1)
  animal_type = messages.StringField(2)
  color = messages.StringField(3)

class SendReportRequest(messages.Message):
  latitude = messages.FloatField(1)
  longitude = messages.FloatField(2)
  status = messages.EnumField(ReportStatus, 3)
  report_type = messages.EnumField(ReportType, 4)
  group_ids = messages.StringField(5, repeated=True)
  description = messages.MessageField(AnimalDescription, 6)

class SendReportResponse(messages.Message):
  report_id = messages.StringField(1)
    
class RoadkillReportResponse(messages.Message):
  latitude = messages.FloatField(1)
  longitude = messages.FloatField(2)
  timestamp = messages.StringField(3)
  status = messages.EnumField(ReportStatus, 4)
  report_type = messages.EnumField(ReportType, 5)
  report_id = messages.StringField(6)
  description = messages.MessageField(AnimalDescription, 7)
  group_ids = messages.StringField(8, repeated=True)
    
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
  reporting_criteria = messages.StringField(3)
  latitude = messages.FloatField(4)
  longitude = messages.FloatField(5)
  radius = messages.FloatField(6)
    
class CreateControlGroupResponse(messages.Message):
  group_id = messages.StringField(1)

class ControlGroupResponse(messages.Message):
  name = messages.StringField(1)
  email = messages.StringField(2)
  reporting_criteria = messages.StringField(3)
  latitude = messages.FloatField(4)
  longitude = messages.FloatField(5)
  radius = messages.FloatField(6)
  group_id = messages.StringField(7)
    
class GetNearbyGroupsRequest(messages.Message):
  latitude = messages.FloatField(1)
  longitude = messages.FloatField(2)
        
class GetNearbyGroupsResponse(messages.Message):
  groups = messages.MessageField(ControlGroupResponse, 1, repeated=True)

# NDB models.
class RoadkillReport(ndb.Model):
  latitude=ndb.FloatProperty()
  longitude=ndb.FloatProperty()
  timestamp=ndb.DateTimeProperty(auto_now_add=True)
  report_type=msgprop.EnumProperty(ReportType)
  status=msgprop.EnumProperty(ReportStatus)
  description=msgprop.MessageProperty(AnimalDescription)
  group_ids=ndb.StringProperty(repeated=True)
    
class ControlGroup(ndb.Model):
  name=ndb.StringProperty()
  email=ndb.StringProperty()
  reporting_criteria=ndb.StringProperty()
  latitude=ndb.FloatProperty()
  longitude=ndb.FloatProperty()
  radius=ndb.FloatProperty()