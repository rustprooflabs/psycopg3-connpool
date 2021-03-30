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
else:
    log_level = logging.INFO
    logging.getLogger('psycopg3').setLevel(logging.WARNING)

logging.basicConfig(filename=config.LOG_PATH,
                    level=log_level,
                    format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')




from webapp import routes

app.logger.info('Program ready...')
