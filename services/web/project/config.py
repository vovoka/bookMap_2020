import os
# from dotenv import load_dotenv
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):

    FLASK_APP = os.getenv('FLASK_APP')

    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite://")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.urandom(32)

    # Image upload settings
    MAX_IMAGE_FILESIZE = 2 * 1024 * 1024  # first multiplier = 1 Mb
    IMAGE_UPLOADS = os.path.join(basedir, 'static/covers')
    IMAGE_TARGET_SIZE = '110x160'  # i.e. width = 100 px, height = 160 px
    ALLOWED_IMAGE_EXTENSIONS = ["JPEG", "JPG", "PNG", "GIF"]

    # Map settings
    DEFAULT_MAP_COORDINADES = (50.4547, 30.520)  # Kyiv

    # Other
    CHECK_EXPIRED_BOOK_INSTANCES = True
    EXPIRATION_PERIOD_DAYS = 30
    NEW_BOOKS_PER_DAY_LIMIT = 3

    # Google OAUth2 credentials
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", None)
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", None)

    # email
    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_PORT = int(os.getenv('MAIL_PORT') or 25)
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True

    # GOOGLE_API_KEY for Google books. Expired at 12.09.20 (?)
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

    BASEDIR = os.path.join(basedir, '/')
