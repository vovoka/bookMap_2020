# from flask import Flask
from flask import Flask
from config import Config
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging.handlers import RotatingFileHandler
import os


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


# Flask-Admin
from flask_admin import Admin
from flask_admin.contrib.fileadmin import FileAdmin
from flask_admin.contrib.sqla import ModelView
from app.models import Book, BookInstance, User

class AdminUserView(ModelView):
    ''' Used as a view wrapper in Flask-admin view. '''
    can_create = True
    page_size = 50  # the number of entries to display on the list view


admin = Admin(app, template_mode='bootstrap3')

admin.add_view(AdminUserView(User, db.session, name='Users'))
admin.add_view(AdminUserView(Book, db.session, name='Books'))
admin.add_view(AdminUserView(BookInstance, db.session, name='BookInstances'))

path = os.path.join(os.path.dirname(__file__), 'static')  # manage files
admin.add_view(FileAdmin(path, '/static/', name='Files'))


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
