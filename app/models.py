
from hashlib import md5
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import app, db, login


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    avatar = db.Column(db.String(200))
    is_active = db.Column(db.Boolean, default=False)
    tokens = db.Column(db.Text) # need it?
    created_at = db.Column(db.DateTime, default=datetime.utcnow())

    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    BookInstance = db.relationship('BookInstance', backref='xxxx',
                                   lazy='dynamic'
                                   )  # ? TODO neet it? fix backref
    messages_sent = db.relationship('Message',
                                    foreign_keys='Message.sender_id',
                                    backref='author', lazy='dynamic')
    messages_received = db.relationship('Message',
                                        foreign_keys='Message.recipient_id',
                                        backref='recipient', lazy='dynamic')
    last_message_read_time = db.Column(
        db.DateTime, default=datetime(1900, 1, 1))

    def new_messages(self):
        last_read_time = self.last_message_read_time or datetime(1900, 1, 1)
        return Message.query.filter_by(recipient=self).filter(
            Message.timestamp > last_read_time).count()

    def __repr__(self):
        return '<User {}>'.format(self.username)


class BookInstance(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    price = db.Column(db.Integer)
    condition = db.Column(db.Integer)
    description = db.Column(db.String(2000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'))
    is_active = db.Column(db.Boolean(), default=True)
    activation_time = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<BookInstance {}>'.format(self.description)


class Book(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    isbn_10 = db.Column(db.Integer())
    isbn_13 = db.Column(db.Integer())
    title = db.Column(db.String(140))
    author = db.Column(db.String(140))
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    instance_counter = db.Column(db.Integer, default=0)
    # TODO fix backref
    BookInstance = db.relationship(
        'BookInstance', backref='aaaaa', lazy='dynamic')

    def __repr__(self):
        return '<Book {}>'.format(self.title)


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'))
    book_instance_id = db.Column(db.Integer, default=0)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    exists_for_sender = db.Column(db.Integer, default=1)
    exists_for_recipient = db.Column(db.Integer, default=1)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return '<Message {}>'.format(self.body)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))
