import test_util
test_util.fix_paths()

import unittest

from google.appengine.ext import ndb
from google.appengine.api import memcache
from google.appengine.ext import testbed

import models
from report_manager import ReportManager

LOC1 = (33.581396, -101.891970)  # In Lubbock.
LOC2 = (33.576782, -101.867600)  # In Lubbock.
LOC3 = (33.563708, -101.898767)  # In Lubbock.
LOC4 = (33.971235, -101.610316)  # Far from Lubbock.

class ReportManagerTest(unittest.TestCase):

  def __init__(self, *args, **kwargs):
    super(ReportManagerTest, self).__init__(*args, **kwargs)
    self.manager = ReportManager()

  def setUp(self):
    self.testbed = testbed.Testbed()
    
    self.testbed.activate()
    self.testbed.init_datastore_v3_stub()
    self.testbed.init_memcache_stub()
    self.testbed.init_search_stub()
    ndb.get_context().clear_cache()
    
  def tearDown(self):
    self.testbed.deactivate()
  
  def test_create_and_lookup(self):
    request = self._make_report_request()
    response = self.manager.create_report(request)
    report = self.manager.get_report(response.report_id)
    self.assertEqual(request.latitude, report.latitude)
    self.assertEqual(request.longitude, report.longitude)
    self.assertEqual(request.status, report.status)
    self.assertEqual(request.report_type, report.report_type)

  def test_update(self):
    request = self._make_report_request()
    response = self.manager.create_report(request)
    request.status = models.ReportStatus.IN_PROGRESS
    self.manager.update_report(request, response.report_id)
    report = self.manager.get_report(response.report_id)
    self.assertEqual(request.latitude, report.latitude)
    self.assertEqual(request.longitude, report.longitude)
    self.assertEqual(request.status, report.status)
    self.assertEqual(request.report_type, report.report_type)

  def test_lookup_radius(self):
    request = self._make_report_request()
    response = self.manager.create_report(request)
    report_id1 = response.report_id
    request.latitude = LOC2[0]
    request.longitude = LOC2[1]
    response = self.manager.create_report(request)
    report_id2 = response.report_id
    request.latitude = LOC3[0]
    request.longitude = LOC3[1]
    response = self.manager.create_report(request)
    report_id3 = response.report_id
    request.latitude = LOC4[0]
    request.longitude = LOC4[1]
    response = self.manager.create_report(request)
    report_id4 = response.report_id
    radius_request = models.GetRadiusReportsRequest(latitude=LOC1[0], longitude=LOC1[1], limit=5, radius=10)
    radius_response = self.manager.get_report_in_radius(radius_request)
    in_radius_ids = [report_id1, report_id2, report_id3]
    for report in radius_response.reports:
      self.assertTrue(report.report_id in in_radius_ids)

  def _make_report_request(self):
    lat = LOC1[0]
    lon = LOC1[1]
    request = models.SendReportRequest(latitude=lat, longitude=lon, status=models.ReportStatus.OPEN, report_type=models.ReportType.INJURED)
    return request

if __name__ == '__main__':
  unittest.main()