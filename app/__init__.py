from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

# create app
app = Flask(__name__)

# add config
app.config.from_object(Config)

# register services
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)

from app import routes, models, errors

def create_app():
    app = Flask(__name__)
    
    db = SQLAlchemy(app)
    migrate = Migrate(app, db)
    login = LoginManager(app)

    from . import db
    db.init_app(app)

    return app


from app import routes, models