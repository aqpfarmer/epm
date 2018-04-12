import sys
sys.path.insert(0, "/var/www/epm")
sys.stdout = sys.stderr

from epm import app
application = app
