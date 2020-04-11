# from app import app
from app import db
from app.models import User, Book, BookInstance, Message
from random import random, randint
from sqlalchemy import or_, and_

#  ------------  GENERAL DB ------------------


def make_db_data(db):
    """ Fill DB with users, Books, BookInstances """
    db.create_all()
    # create users
    latitude = 50.4547
    longitude = 30.520
    for i in 'cdefghikz':
        user = User(
            username=i*3,
            email=i*3 + '@gmail.com',
            latitude=latitude + (random() - 0.5)/10,
            longitude=longitude + (random() - 0.5)/10,
            about_me='No info about the uses yet.'
        )
        user.set_password(i*3)
        db.session.add(user)
    db.session.commit()
    # create boooks
    books = [
        ('In Search of Lost Time', 'Marcel Proust'),
        ('Ulysses', 'James Joyce'),
        ('Don Quixote', 'Miguel de Cervantes'),
        ('The Great Gatsby', 'F. Scott Fitzgerald'),
        ('One Hundred Years of Solitude', 'Gabriel Garcia Marquez'),
        ('Moby Dick', 'Herman Melville'),
        ('War and Peace', 'Leo Tolstoy'),
        ('Lolita', 'Vladimir Nabokov'),
        ('Hamlet', 'William Shakespeare'),
        ('The Catcher in the Rye', 'J. D. Salinger'),
        ('The Odyssey', 'Homer'),
        ('The Brothers Karamazov', 'Fyodor Dostoyevsky'),
        ('Crime and Punishment', 'Fyodor Dostoyevsky'),
        ('Madame Bovary', 'Gustave Flaubert'),
        ('The Divine Comedy', 'Dante Alighieri'),
    ]
    for book in books:
        book = Book(title=book[0], author=book[1])
        db.session.add(book)
    db.session.commit()
    # create boook instances
    for book_instance in range(25):
        book_instance = BookInstance(
            details=randint(1, 15),
            owner_id=randint(1, 8),
            price=randint(20, 200),
            condition=randint(1, 12),
            description='Lorem ipsum...'
        )
        db.session.add(book_instance)
    db.session.commit()


def clear_db_data(db):
    """ clear all rows from listed db tables """
    tables = [BookInstance, Book, User]
    for table in tables:
        db.session.query(table).delete()
    db.session.commit()


#  ------------  BOOK ------------------


def create_book(title: str, author: str) -> object:
    if not book_exist(title, author):
        book = Book(title=title, author=author)
        db.session.add(book)
        db.session.commit()
        print('Book created "{title}" "{author}"', flush=True)
        return book


def book_exist(title: str, author: str) -> bool:
    """ Check if book with incoming attributes is in db """
    return bool(Book.query.filter_by(
        title=title,
        author=author
    ).first())


def get_book_id(title: str, author: str):
    """ Returns Book.id or None """
    book = Book.query.filter_by(
        title=title,
        author=author
    ).first()
    book_id = book.id if book else None
    res = int(book_id) if book_id else None
    return res


def get_books_by_user_id(user_id) -> list:
    """ Returns list of Book objects """
    books = (db.session.query(
        User.username,
        Book.title,
        Book.author,
    )
        .filter(BookInstance.owner_id == user_id)
        .filter(BookInstance.details == Book.id))
    return books


def get_all_book_instances() -> list:
    """ Returns all BookInstances """
    book_instances = (db.session.query(
        User.username,
        Book.title,
        Book.author,
        BookInstance.id,
        BookInstance.price,
        BookInstance.condition,
        BookInstance.description,
    )
        .filter(BookInstance.owner_id == User.id)
        .filter(BookInstance.details == Book.id))
    return book_instances

#  ------------  BOOK INSTANCE ------------------


def create_book_instance(price, condition, description, owner_id, book_id):
    """
    Add book instance to db

    Return new object id
    """
    # create book instance
    book_instance = BookInstance(
        details=book_id,
        owner_id=owner_id,
        price=price,
        condition=condition,
        description=description
    )
    db.session.add(book_instance)
    db.session.commit()
    return book_instance


def delete_book_instance_by_id(book_instance_id: str) -> None:
    BookInstance.query.filter_by(id=book_instance_id).delete()
    db.session.commit()

def get_book_instance_by_id(book_instance_id: str) -> object:
    """ Returns BookInstance object if exists in DB or None"""
    book_instance = (db.session.query(
        User.username,
        Book.title,
        Book.author,
        BookInstance.id,
        BookInstance.owner_id,
        BookInstance.price,
        BookInstance.condition,
        BookInstance.description,
        BookInstance.details,
    )
        .filter(BookInstance.owner_id == User.id)
        .filter(BookInstance.id == book_instance_id)
        .filter(BookInstance.details == Book.id)
        .first_or_404())
    return book_instance


def get_book_instances_by_user_id(user_id) -> list:
    """ Returns list of BookInstance objects """
    book_instances = (db.session.query(
        User.username,
        User.id,
        Book.title,
        Book.author,
        BookInstance.id,
        BookInstance.price,
        BookInstance.condition,
        BookInstance.description,
    )
        .filter(BookInstance.owner_id == user_id)
        .filter(User.id == user_id)
        .filter(BookInstance.details == Book.id)
        .order_by(BookInstance.id.desc())
        .all())
    return book_instances


def get_book_instances_by_book_id(book_id) -> list:
    """ Returns list of BookInstance objects """
    book_instances = (db.session.query(
        User.username,
        User.id,
        BookInstance.id,
        BookInstance.owner_id,
        BookInstance.price,
        BookInstance.condition,
        BookInstance.description,
    )
        .filter(BookInstance.details == book_id)
        .filter(BookInstance.owner_id == User.id)
        .order_by(BookInstance.id.desc())
        .all())
    return book_instances

#  ------------ USER ------------------


#  ------------ MESSAGE ------------------

def get_message(message_id) -> object:
    """ Returns Message object """
    message = Message.query.filter_by(id=message_id).first_or_404()
    return message

def get_messages_by_user(user_id):
    """ Returns non-deleted users Messages (both sent and received) """
    messages = (
        Message.query
        .filter(
            or_(
                and_(Message.sender_id == user_id,
                     Message.exists_for_sender == 1),
                and_(Message.recipient_id == 1,
                     Message.exists_for_recipient == 1)
                )
        )
        .order_by(Message.timestamp.desc())
    )
    return messages
