import logging
from flask import Flask
from webapp import config

# App settings
app = Flask(__name__)
app.config['DEBUG'] = config.APP_DEBUG
app.config['SECRET_KEY'] = config.APP_SECRET_KEY
app.config['WTF_CSRF_ENABLED'] = True

if config.APP_DEBUG:
    log_level = logging.DEBUG
    logging.getLogger('psycopg3').setLevel(logging.INFO)
else:
    log_level = logging.INFO
    # Don't display INFO from psycopg3, too noisy for app logs
    # If addressed this can be removed: https://github.com/psycopg/psycopg3/issues/43
    logging.getLogger('psycopg3').setLevel(logging.WARN)


logging.basicConfig(filename=config.LOG_PATH,
                    level=log_level,
                    format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')


from webapp import routes

app.logger.debug('psycopg3-connpool webapp ready...')
