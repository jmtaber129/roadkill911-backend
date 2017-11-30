import models
from google.appengine.ext import ndb
from google.appengine.api import search

GROUP_INDEX_NAME = 'groupsearch'
GROUP_ID = 'group_id'

MAX_RADIUS = 200 * models.METERS_PER_MILE

class ControlGroupManager:
  def create_group(self, request):
    if request.radius > MAX_RADIUS:
      # Error handling
      pass
    group = models.ControlGroup(name=request.name, 
      email=request.email, 
      reporting_criteria=request.reporting_criteria, 
      latitude=request.latitude, 
      longitude=request.longitude, 
      radius=request.radius*models.METERS_PER_MILE)
    group_id = group.put().urlsafe()
    
    geopoint = search.GeoPoint(request.latitude, request.longitude)
    index_fields = [
      search.AtomField(name=GROUP_ID, value=group_id),
      search.GeoField(name=models.LOCATION, value=geopoint),
      search.NumberField(name=models.RADIUS, 
        value=request.radius*models.METERS_PER_MILE)
    ]
    doc = search.Document(doc_id=group_id, fields=index_fields)
    search.Index(name=GROUP_INDEX_NAME).put(doc)
    
    return models.CreateControlGroupResponse(group_id=group_id)
    
  def get_nearby_groups(self, request):
    groups = []
    query_string = 'distance({}, geopoint({},{})) < {}'.format(models.LOCATION, 
      request.latitude, 
      request.longitude, 
      MAX_RADIUS)
    radius_expression = search.FieldExpression(name='dist', 
      expression='distance({}, geopoint({},{})) - radius'.format(
        models.LOCATION, request.latitude, request.longitude))
    query_options = search.QueryOptions(
      returned_expressions=[radius_expression])
    query = search.Query(query_string=query_string, options=query_options)
    results = search.Index(GROUP_INDEX_NAME).search(query)
    
    for doc in results:
      if doc.expressions[0].value > 0:
        # Input location outside of group's radius.
        continue;
      group_id = doc.doc_id
      group_key = ndb.Key(urlsafe=group_id)
      ndb_group = group_key.get()
      group = models.CreateControlGroupRequest(email=ndb_group.email, 
        name=ndb_group.name, 
        reporting_criteria=ndb_group.reporting_criteria,
        latitude=ndb_group.latitude, 
        longitude=ndb_group.longitude, 
        radius=ndb_group.radius / models.METERS_PER_MILE)
      groups.append(group)
    resp = models.GetNearbyGroupsResponse(groups=groups)
    return resp

  def get_group(self, group_id):
    group_key = ndb.Key(urlsafe=group_id)
    ndb_group = group_key.get()
    return ndb_group
