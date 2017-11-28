import models
from google.appengine.ext import ndb
from google.appengine.api import search

REPORT_INDEX_NAME = 'reportsearch'
REPORT_ID = 'report_id'

class ReportManager:
  def create_report(self, request):
    report = models.RoadkillReport(latitude=request.latitude, longitude=request.longitude, status=models.ReportStatus.OPEN)
    report_id = report.put().urlsafe()
    
    geopoint = search.GeoPoint(request.latitude, request.longitude)
    index_fields = [
      search.AtomField(name=REPORT_ID, value=report_id),
      search.GeoField(name=models.LOCATION, value=geopoint)
    ]
    doc = search.Document(doc_id=report_id, fields=index_fields)
    search.Index(name=REPORT_INDEX_NAME).put(doc)
    
    return models.SendReportResponse(report_id=report_id)
    
  def get_report(self, report_id):
    report_key = ndb.Key(urlsafe=report_id)
    report = report_key.get()
    resp = models.RoadkillReportResponse(latitude=report.latitude, longitude=report.longitude, timestamp=str(report.timestamp), status=report.status, report_id=report_id)
    return resp
    
  def get_report_in_radius(self, request):
    reports = []
    query = "distance({}, geopoint({},{})) < {}".format(models.LOCATION, request.latitude, request.longitude, request.radius * models.METERS_PER_MILE)
    results = search.Index(REPORT_INDEX_NAME).search(query)
    for doc in results:
      report_id = doc.doc_id
      report_key = ndb.Key(urlsafe=report_id)
      ndb_report = report_key.get()
      report = models.RoadkillReportResponse(latitude=ndb_report.latitude, longitude=ndb_report.longitude, timestamp=str(ndb_report.timestamp), status=ndb_report.status, report_id=report_id)
      reports.append(report)
    resp = models.GetRadiusReportsResponse(reports=reports)
    return resp
    
  def update_report(self, request, report_id):
    report_key = ndb.Key(urlsafe=report_id)
    report = report_key.get()
    report.status = request.status
    report.put()
    return models.SendReportResponse(report_id=report_id)
