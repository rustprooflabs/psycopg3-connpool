import os
import logging

APP_NAME = 'psycopg3-connpool'

# Set to False to force reporting queries to share pool with non-reporting queries
REPORTING_POOL = True

POOL_MIN_SIZE = 1
POOL_MAX_SIZE = 10
POOL_MAX_IDLE = 60
POOL_STAT_SLEEP = 300


if not REPORTING_POOL:
    pool_max_size += 5


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
    #LOGGER.warning(ERR_MSG)
    print(ERR_MSG)
    APP_SECRET_KEY = 'S$332sgajg9GHKL14jklsjfkjasglmssajfsdgGADAAJj77j@neHMld'

try:
    DATABASE_STRING = os.environ['PG_CONN']
except KeyError:
    key_msg = 'Database environment variable not set.  Need PG_CONN string'
    sys.exit(key_msg)


try:
    APP_DEBUG_RAW = os.environ['APP_DEBUG']
    if APP_DEBUG_RAW == 'False':
        APP_DEBUG = False
    else:
        APP_DEBUG = True
except KeyError:
    APP_DEBUG = False

