from . import app, db
from .models import User, Book, BookInstance, Message

# @app.shell_context_processor
# def make_shell_context():
#     return {'db': db, 'User': User, 'Book': Book, 'BookInstance': BookInstance, 'Message': Message}
