# from flask import Flask
from flask import Flask, request
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from flask_moment import Moment
import os
import logging
from logging.handlers import RotatingFileHandler
from authlib.integrations.flask_client import OAuth
from config import Config
from flask_mail import Mail

app = Flask(__name__)
app.secret_key = '!secret'

app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'
# login.login_message = 'Please log in to access this page.'
bootstrap = Bootstrap(app)
moment = Moment(app)
mail = Mail(app)

# if not app.debug:
if True:

    # logger
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/booklib.log', maxBytes=10240,
                                       backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info('BookLib startup')


from app import routes, models, errors
