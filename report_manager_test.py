import test_util
test_util.fix_paths()

import unittest

from google.appengine.ext import ndb
from google.appengine.api import memcache
from google.appengine.ext import testbed

import models
from report_manager import ReportManager

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

  def _make_report_request(self):
    lat = 33.581396
    lon = -101.891970
    request = models.SendReportRequest(latitude=lat, longitude=lon, status=models.ReportStatus.OPEN)
    return request

if __name__ == '__main__':
  unittest.main()