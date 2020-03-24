
from hashlib import md5
from datetime import datetime
from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    BookInstance = db.relationship('BookInstance', backref='xxxx',
                                   lazy='dynamic'
                                   )  # ? TODO neet it? fix backref

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User {}>'.format(self.username)


class BookInstance(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    price = db.Column(db.Integer)
    condition = db.Column(db.Integer)
    description = db.Column(db.String(2000))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    details = db.Column(db.Integer, db.ForeignKey('book.id'))

    def __repr__(self):
        return '<BookInstance {}>'.format(self.description)


class Book(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    title = db.Column(db.String(140))
    author = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    # TODO fix backref
    BookInstance = db.relationship(
        'BookInstance', backref='aaaaa', lazy='dynamic')

    def __repr__(self):
        return '<Book {}>'.format(self.title)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


# def make_db_data(db):
#     """ Fill DB with users, Books, BookInstances """

#     # create users
#     latitude = 50.4547
#     longitude = 30.520
#     for i in 'cdefghikz':
#         user = User(
#             username=i*3,
#             email=i*3 + '@gmail.com',
#             latitude=latitude + (random() - 0.5)/10,
#             longitude=longitude + (random() - 0.5)/10,
#             about_me='No info about the uses yet.'
#         )
#         user.set_password(i*3)
#         db.session.add(user)
#     db.session.commit()

#     # create boooks
#     books = [
#         ('In Search of Lost Time', 'Marcel Proust'),
#         ('Ulysses', 'James Joyce'),
#         ('Don Quixote', 'Miguel de Cervantes'),
#         ('The Great Gatsby', 'F. Scott Fitzgerald'),
#         ('One Hundred Years of Solitude', 'Gabriel Garcia Marquez'),
#         ('Moby Dick', 'Herman Melville'),
#         ('War and Peace', 'Leo Tolstoy'),
#         ('Lolita', 'Vladimir Nabokov'),
#         ('Hamlet', 'William Shakespeare'),
#         ('The Catcher in the Rye', 'J. D. Salinger'),
#         ('The Odyssey', 'Homer'),
#         ('The Brothers Karamazov', 'Fyodor Dostoyevsky'),
#         ('Crime and Punishment', 'Fyodor Dostoyevsky'),
#         ('Madame Bovary', 'Gustave Flaubert'),
#         ('The Divine Comedy', 'Dante Alighieri'),
#     ]
#     for book in books:
#         book = Book(title=book[0], author=book[1])
#         db.session.add(book)
#     db.session.commit()

#     # create boook instances
#     for book_instance in range(25):
#         book_instance = BookInstance(
#             details=randint(1, 15),
#             owner_id=randint(1, 8),
#             price=randint(20, 200),
#             condition=randint(1, 12),
#             description='Lorem ipsum...'
#         )
#         db.session.add(book_instance)
#     db.session.commit()


# def clear_db_data(db):
#     """ clear all rows from listed db tables """
#     tables = [BookInstance, Book, User]
#     for table in tables:
#         db.session.query(table).delete()
#     db.session.commit()
