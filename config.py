import os
from dotenv import load_dotenv
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):

    # Load secrets from dotenv
    dotenv_path = os.path.join(basedir, '.env')
    load_dotenv(dotenv_path)

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.urandom(32)

    # Image upload settings
    MAX_IMAGE_FILESIZE = 2 * 1024 * 1024  # first multiplier = 1 Mb
    IMAGE_UPLOADS = os.path.join(basedir, 'app/static/covers')
    IMAGE_TARGET_SIZE = '110x160'  # i.e. width = 100 px, height = 160 px
    ALLOWED_IMAGE_EXTENSIONS = ["JPEG", "JPG", "PNG", "GIF"]

    # Map settings
    DEFAULT_MAP_COORDINADES = (50.4547, 30.520)  # Kyiv

    # Other
    CHECK_EXPIRED_BOOK_INSTANCES = True
    EXPIRATION_PERIOD_DAYS = 30
    NEW_BOOKS_PER_DAY_LIMIT = 3

    # Google OAUth2 credentials
    GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", None)
    GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", None)

    # email
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True

    # GOOGLE_API_KEY for Google books. Expired at 12.09.20 (?)
    GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
