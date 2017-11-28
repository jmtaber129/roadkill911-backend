def fix_paths():
  import sys
  import os
  sys.path.insert(1, '/home/jtaber/bin/google-cloud-sdk/platform/google_appengine')
  import dev_appserver
  dev_appserver.fix_sys_path()