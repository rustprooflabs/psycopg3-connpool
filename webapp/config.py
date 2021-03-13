import os
import logging

APP_NAME = 'psycopg3-connpool-webapp'

min_size = 4
max_size = 30
max_idle = 60


LOG_FORMAT = '%(levelname)s - %(asctime)s - %(name)s - %(message)s'
LOGGER = logging.getLogger(__name__)

CURR_PATH = os.path.abspath(os.path.dirname(__file__))
PROJECT_BASE_PATH = os.path.abspath(os.path.join(CURR_PATH, os.pardir))

try:
    LOG_PATH = os.environ['LOG_PATH']
except KeyError:
    LOG_PATH = PROJECT_BASE_PATH + '/webapp.log'


# Required for CSRF protection in Flask, please change to something secret!
try:
    APP_SECRET_KEY = os.environ['APP_SECRET_KEY']
except KeyError:
    ERR_MSG = '\nSECURITY WARNING: To ensure security please set the APP_SECRET_KEY'
    ERR_MSG += ' environment variable.\n'
    LOGGER.warning(ERR_MSG)
    print(ERR_MSG)
    APP_SECRET_KEY = 'S$332sgajg9GHKL14jklsjfkjasglmssajfsdgGADAAJj77j@neHMld'

try:
    DATABASE_STRING = os.environ['PG_CONN']
except KeyError:
    key_msg = 'Database environment variable not set.  Need PG_CONN string'
    sys.exit(key_msg)

