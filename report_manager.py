import models
from control_group_manager import ControlGroupManager
from google.appengine.ext import ndb
from google.appengine.api import search
from google.appengine.api import mail

REPORT_INDEX_NAME = 'reportsearch'
REPORT_ID = 'report_id'

class ReportManager:
  def __init__(self):
    self.group_manager = ControlGroupManager()

  def create_report(self, request):
    report = models.RoadkillReport(latitude=request.latitude, 
      longitude=request.longitude, 
      status=models.ReportStatus.OPEN,
      report_type=request.report_type,
      description=request.description,
      group_ids=request.group_ids)
    report_id = report.put().urlsafe()
    
    geopoint = search.GeoPoint(request.latitude, request.longitude)
    index_fields = [
      search.AtomField(name=REPORT_ID, value=report_id),
      search.GeoField(name=models.LOCATION, value=geopoint)
    ]
    doc = search.Document(doc_id=report_id, fields=index_fields)
    search.Index(name=REPORT_INDEX_NAME).put(doc)
    
    # TODO: Get information for animal control group IDs submitted.

    map_image_link = ('https://maps.googleapis.com/maps/api/staticmap?'
      'markers={},{}&zoom=14&size=640x400').format(
        request.latitude, request.longitude)

    report_page = ("https://roadkill911-180223.appspot.com/#/"
      "view_report/{}").format(report_id)

    # TODO: Send email(s) to animal control groups.
    
    email_body = """<html>
      <body>
      <p>Roadkill911 control group,</p>

      <p>A new report has been submitted to your group.</p>

      <p>Report link: {}</p>

      <img width=640 height=400 src="{}"/>

      <p>--Roadkill911</p>
      </body>
      </html>
      """.format(report_page, map_image_link)

    for group_id in request.group_ids:
      group = self.group_manager.get_group(group_id)
      if group.email:
        email = mail.EmailMessage(
          sender='noreply@roadkill911-180223.appspotmail.com',
          to=group.email,
          subject='New Roadkill911 Report')

        email.html = email_body

        email.send()

    return models.SendReportResponse(report_id=report_id)
    
  def get_report(self, report_id):
    report_key = ndb.Key(urlsafe=report_id)
    report = report_key.get()
    resp = models.RoadkillReportResponse(latitude=report.latitude, 
      longitude=report.longitude, 
      timestamp=str(report.timestamp), 
      status=report.status, 
      report_type=report.report_type, 
      report_id=report_id,
      description=report.description,
      group_ids=report.group_ids)
    return resp
    
  def get_report_in_radius(self, request):
    reports = []
    query = "distance({}, geopoint({},{})) < {}".format(models.LOCATION, 
      request.latitude, 
      request.longitude, 
      request.radius * models.METERS_PER_MILE)
    results = search.Index(REPORT_INDEX_NAME).search(query)
    for doc in results:
      report_id = doc.doc_id
      report_key = ndb.Key(urlsafe=report_id)
      ndb_report = report_key.get()
      report = models.RoadkillReportResponse(latitude=ndb_report.latitude, 
        longitude=ndb_report.longitude, 
        timestamp=str(ndb_report.timestamp), 
        status=ndb_report.status, 
        report_type=ndb_report.report_type, 
        report_id=report_id,
        description=ndb_report.description,
        group_ids=ndb_report.group_ids)
      reports.append(report)
    resp = models.GetRadiusReportsResponse(reports=reports)
    return resp
    
  def update_report(self, request, report_id):
    report_key = ndb.Key(urlsafe=report_id)
    report = report_key.get()
    report.status = request.status
    report.put()
    return models.SendReportResponse(report_id=report_id)
