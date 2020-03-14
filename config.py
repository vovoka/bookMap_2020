import os
basedir = os.path.abspath(os.path.dirname(__file__))



class Config(object):

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.urandom(32)

    # image upload settings
    MAX_IMAGE_FILESIZE = 2 * 1024 * 1024 # first multiplier = 1 Mb
    IMAGE_UPLOADS = "/home/vk/Desktop/2020-02-07_book_v8/app/static/covers"
    ALLOWED_IMAGE_EXTENSIONS = ["JPEG", "JPG", "PNG", "GIF"]