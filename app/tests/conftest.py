import os

if "." not in os.sys.path:
    os.sys.path.insert(0, ".")

from app.tests.fixtures.fixtures import *
from app.tests.fixtures.mock_db_fixtures import *