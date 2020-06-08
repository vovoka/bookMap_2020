# from app import app
from app import db
from app.models import User, Book, BookInstance, Message
from random import random, randint
from sqlalchemy import or_, and_, desc
import csv
from datetime import datetime, timedelta


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
            about_me='No info about the user yet.'
        )
        user.set_password(i*3)
        db.session.add(user)
    db.session.commit()

    # import books from file & create in db
    with open('test_books_data.csv', newline='') as csvfile:
        book_reader = csv.reader(csvfile, delimiter=',', quotechar="'")
        for book in book_reader:
            book = Book(title=book[0], author=book[1], isbn=book[2])
            db.session.add(book)
        db.session.commit()

    # create boook instances
    for book_instance in range(25):
        book_id = randint(1, 15)
        book_instance = BookInstance(
            book_id=book_id,
            owner_id=randint(1, 8),
            price=randint(20, 200),
            condition=randint(1, 12),
            description='Lorem ipsum...'
        )
        incr_instance_counter(book_id)
        db.session.add(book_instance)
    db.session.commit()


def clear_db_data(db):
    """ clear all rows from listed db tables """
    tables = [BookInstance, Book, User, Message]
    for table in tables:
        db.session.query(table).delete()
    db.session.commit()


#  ------------  BOOK ------------------


def get_books_by_kw(key_word):

    search = "%{}%".format(key_word)
    # todo fix request contained part of Author and part of book_title returns None
    # for example 'Hamlet William' --> None
    books_by_title = Book.query.filter(Book.title.like(search)).all()
    if books_by_title == []:
        books_by_author = Book.query.filter(Book.author.like(search)).all()
        return books_by_author
    return books_by_title


def create_book(title: str, author: str, isbn=0) -> object:
    if not book_exist(title, author):
        book = Book(title=title, author=author, isbn=isbn)
        db.session.add(book)
        db.session.commit()
        print('Book created "{title}" "{author}" isbn={isbn}', flush=True)
        return book


def book_exist(title: str, author: str, isbn=0) -> bool:
    """ Check if book with incoming attributes is in db """
    if isbn:
        return bool(Book.query.filter_by(
            isbn=isbn).first())
    return bool(Book.query.filter_by(
        title=title,
        author=author).first())


def get_book_id(title: str, author: str):
    """ Returns Book.id or None """
    book = Book.query.filter_by(
        title=title,
        author=author).first()
    book_id = book.id if book else None
    res = int(book_id) if book_id else None
    return res


def get_books_by_user_id(user_id) -> list:
    """ Returns list of Book objects """
    books = (db.session.query(
        User.username,
        Book.title,
        Book.author,
        Book.isbn)
        .filter(BookInstance.owner_id == user_id)
        .filter(BookInstance.book_id == Book.id))
    return books


def get_book(id) -> object:
    book = Book.query.filter_by(
        id=id).first()
    return book


def get_book_by_isbn(isbn) -> object:
    book = Book.query.filter_by(
        isbn=isbn).first()
    return book


def incr_instance_counter(book_id) -> int:
    """ Icrement book.instance_counter by 1.
    Return new value (int)"""
    book = Book.query.filter_by(id=book_id).first()
    book.instance_counter += 1
    db.session.commit()
    return book.instance_counter


def decr_instance_counter(book_id) -> int:
    """ Decrement book.instance_counter by 1. Return new value (int)"""
    book = Book.query.filter_by(id=book_id).first()
    if book.instance_counter > 0:
        book.instance_counter -= 1
        db.session.commit()
        return book.instance_counter
    raise ValueError(f'instance_counter Value error for book_id={book_id}')

#  ------------  BOOK INSTANCE ------------------


def get_all_book_instances() -> list:
    """ Returns all BookInstances """
    book_instances = (db.session.query(
        User.username,
        Book.title,
        Book.author,
        Book.isbn,
        BookInstance.id,
        BookInstance.price,
        BookInstance.condition,
        BookInstance.description)
        .filter(BookInstance.owner_id == User.id)
        .filter(BookInstance.book_id == Book.id))
    return book_instances


def get_freshest_book_instances(items: int) -> list:
    """ Returns n freshest BookInstances """
    book_instances = (db.session.query(
        User.username,
        User.latitude,
        User.longitude,
        BookInstance.book_id,
        Book.title,
        Book.author,
        Book.isbn,
        BookInstance.id,
        BookInstance.price,
        BookInstance.condition,
        BookInstance.description,
        BookInstance.timestamp)
        .filter(BookInstance.owner_id == User.id)
        .filter(BookInstance.book_id == Book.id)
        .order_by(desc(BookInstance.timestamp)).limit(items).all())
    return book_instances


def create_book_instance(price, condition, description, owner_id, book_id):
    """
    Add book instance to db

    Return new object id
    """
    # create book instance
    book_instance = BookInstance(
        book_id=book_id,
        owner_id=owner_id,
        price=price,
        condition=condition,
        description=description)
    db.session.add(book_instance)
    incr_instance_counter(book_id)
    db.session.commit()
    return book_instance


def update_book_instance(
        book_instance_id,
        price,
        condition,
        description):
    bi_prev_state = get_book_instance_by_id(book_instance_id)
    if (
            price != bi_prev_state.price or
            condition != bi_prev_state.condition or
            description != bi_prev_state.description):
        (
            db.session.query(BookInstance)
            .filter(BookInstance.id == book_instance_id)
            .update(
                {
                    BookInstance.price: price,
                    BookInstance.condition: condition,
                    BookInstance.description: description
                }, synchronize_session=False))
        db.session.commit()


def delete_book_instance_by_id(book_instance_id: str) -> None:
    bi = get_book_instance_by_id(book_instance_id)
    decr_instance_counter(bi.book_id)
    BookInstance.query.filter_by(id=book_instance_id).delete()
    db.session.commit()


def get_book_instance_by_id(book_instance_id: str) -> object:
    """ Returns BookInstance object if exists in DB or None"""
    book_instance = (db.session.query(
        User.username,
        Book.title,
        Book.author,
        Book.isbn,
        BookInstance.id,
        BookInstance.owner_id,
        BookInstance.price,
        BookInstance.condition,
        BookInstance.description,
        BookInstance.book_id,
        BookInstance.is_active)
        .filter(BookInstance.owner_id == User.id)
        .filter(BookInstance.id == book_instance_id)
        .filter(BookInstance.book_id == Book.id)
        .first_or_404())
    return book_instance


def get_book_instances_by_user_id(user_id) -> list:
    """ Returns list of BookInstance objects """
    book_instances = (db.session.query(
        User.username,
        User.id,
        Book.title,
        Book.author,
        Book.isbn,
        BookInstance.id,
        BookInstance.price,
        BookInstance.condition,
        BookInstance.description,
        BookInstance.is_active)
        .filter(BookInstance.owner_id == user_id)
        .filter(User.id == user_id)
        .filter(BookInstance.book_id == Book.id)
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
        BookInstance.is_active)
        .filter(BookInstance.book_id == book_id)
        .filter(BookInstance.owner_id == User.id)
        .order_by(BookInstance.id.desc())
        .all())
    return book_instances


def get_book_instances_id_by_book_id(book_id) -> tuple:
    """ Returns list of BookInstance IDs """
    book_instances_ids = (db.session.query(
        BookInstance.id)
        .filter(BookInstance.book_id == book_id)
        .all())
    book_instances_ids = tuple(el[0] for el in book_instances_ids)
    return book_instances_ids


def deactivate_if_expired(bi_ids: list, expiration_period_days=30) -> None:
    """ Update bi's status active -> inactive in DB if expired.

    Obviously, it's better to run the task separately from user's requests.
    First idea - redis/selery. Hovewer both usually used for postponed
    operations for example after minute delay after some trigger-action.
    So we come to cronjobs. It's simpler and easy implemented with APScheduler
    ...until app factory used.
    If app_factory is implemented than appeared a problem with app_context
     (which is needed for db updating). app_context is not shared.
    See some considerations here https://stackoverflow.com/questions/62171804\
    /add-a-cron-job-using-apscheduler-in-flask-flask-factory/62249027#62249027
    """

    # month_ago = now - 30 days
    expiration_time = datetime.today() - timedelta(days=expiration_period_days)
    expiration_time_timestamp = datetime.timestamp(expiration_time)
    (db.session.query(BookInstance)
     .filter(BookInstance.id.in_(bi_ids))
     .filter(BookInstance.is_active == True)
     .filter(BookInstance.activation_time <= expiration_time_timestamp)
     .update({
         BookInstance.is_active: False,
     }, synchronize_session=False))
    db.session.commit()


def activate_book_instance(book_instance_id):
    (db.session.query(BookInstance)
     .filter(BookInstance.id == book_instance_id)
     .update({
         BookInstance.is_active: True,
         BookInstance.activation_time: datetime.utcnow
     }, synchronize_session=False))
    db.session.commit()


def deactivate_book_instance(book_instance_id):
    (db.session.query(BookInstance)
     .filter(BookInstance.id == book_instance_id)
     .update({BookInstance.is_active: False}, synchronize_session=False))
    db.session.commit()

#  ------------ USER ------------------


def get_user_by_username(username: str) -> object:
    return User.query.filter_by(username=username).first_or_404()


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
                and_(Message.recipient_id == user_id,
                     Message.exists_for_recipient == 1)))
        .order_by(Message.timestamp.desc()))
    return messages
