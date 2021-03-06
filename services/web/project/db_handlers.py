import csv
import os
from datetime import datetime, timedelta
from random import randint, random
from typing import List, Union
from shutil import copyfile, rmtree


from sqlalchemy import and_, desc, or_

from . import db
from .models import Book, BookInstance, Message, User


#  ------------  GENERAL DB ------------------
def make_db_data(
        db,
        # filepath='project/test_books_data.csv',
        filepath='project/data_example/example_data.csv',
        users=15,
        books=15,  # data example is prepared for 15 books only
        book_instances=60,
        latitude=50.4547,
        longitude=30.520) -> None:
    """ Fill DB with Users, Books, BookInstances
    Args:
     - filepath:str filepath to *.csv file to parse to fill db with the data
     - users , books, book_instances, : how many fake to genetate.
       Keep in mind - only 15 book covers are prepared. Better not to change
       'books=15' with no real need.
      - latitude, longitude - basic coordinates. Users location is generated
        around this point.
    """

    if not os.path.exists(filepath):
        return

    # create users
    for i in range(users):
        user = User(
            username='user_' + str(i),
            email='user_' + str(i) + '@gmail.com',
            latitude=latitude + (random() - 0.5) / 3,
            longitude=longitude + (random() - 0.5) / 3,
            about_me='No info about the user yet.'
        )
        db.session.add(user)
    db.session.commit()

    # import books from file & write them into db
    if os.path.exists(filepath):
        with open(filepath, newline='') as csvfile:
            book_reader = csv.reader(csvfile, delimiter=',', quotechar="'")
            for title, author, isbn_13 in book_reader:
                db.session.add(Book(
                    title=title,
                    author=author,
                    isbn_13=isbn_13))
            db.session.commit()

    # create boook instances
    for book_instance in range(book_instances):
        book_id = randint(1, books)
        book_instance = BookInstance(
            book_id=book_id,
            owner_id=randint(1, users),
            price=randint(20, 200),
            condition=randint(1, 4),
            description='Lorem ipsum...',
        )
        incr_instance_counter(book_id)
        db.session.add(book_instance)
    db.session.commit()

    # copy covers to static/covers
    for i in range(16):
        copyfile(
            'project/data_example/example_covers/' + str(i) + '.jpg',  # src
            'project/static/covers/' + str(i) + '.jpg')  # destination filepath


def delete_all_files_in_dir(folder: str):
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))


#  ------------  COMMON ------------------

def obj_counter(_class, days: int = 0) -> int:
    ''' Returns quantity of the class objects created during last X days.
    if days == 0 --> count all objects.
    '''
    if days:
        time_from = (datetime.today() - timedelta(days))
        return _class.query.filter(_class.timestamp > time_from).count()
    return _class.query.count()


#  ------------  BOOK ------------------

def get_books_by_kw(key_word) -> List[Book]:
    """ Returns list of book instances founded by key_words

    Q: why is the loop?
    A: to decrease key_words untill something is found.
    The crutch solves next problem:
    if request contained part of Author and part of book_title returns None
    for example 'Hamlet William' --> None
    It's simple, stupid, yes. Later going to made a search with Elastic
    Current problem: ' rssr Hamlet William' --> None because 'rssr' still not
    found. Split key_word to words and use these words combinations looks
    like a nightmare.
    """

    search = "%{}%".format(key_word)

    def search_attempt(search):
        books_by_title = Book.query.filter(Book.title.like(search)).all()
        if not books_by_title:
            books_by_author = Book.query.filter(Book.author.like(search)).all()
            return books_by_author
        return books_by_title

    search_result = search_attempt(search)

    while ' ' in search and not search_result:
        search = search.rsplit(' ', 1)[0] + '%'
        search_result = search_attempt(search)

    return search_result


def create_book(title: str,
                author: str,
                isbn_10: Union[str, None],
                isbn_13: Union[str, None],
                current_user_id: int,
                ) -> Book:
    book = Book(
        title=title,
        author=author,
        isbn_10=isbn_10,
        isbn_13=isbn_13,
        created_by=current_user_id,
    )
    db.session.add(book)
    db.session.commit()
    return book


def get_book_id(title: str, author: str) -> Union[int, None]:
    """ Returns Book.id or None """
    book = Book.query.filter_by(
        title=title,
        author=author).first()
    book_id = book.id if book else None
    res = int(book_id) if book_id else None
    return res


def get_books_by_user_id(user_id) -> List[Book]:
    """ Returns list of Book objects """
    books = (db.session.query(
        User.username,
        Book.title,
        Book.author,
        Book.isbn_10,
        Book.isbn_13,
    )
        .filter(BookInstance.owner_id == user_id)
        .filter(BookInstance.book_id == Book.id))
    return books


def get_book(book_id) -> Union[Book, None]:
    book = Book.query.filter_by(
        id=book_id).first()
    return book


def get_book_by_isbn_10(isbn_10) -> Union[Book, None]:
    book = Book.query.filter_by(
        isbn_10=isbn_10).first()
    return book


def get_book_by_isbn_13(isbn_13) -> Union[Book, None]:
    book = Book.query.filter_by(
        isbn_13=isbn_13).first()
    return book


def update_book_isbn_10(book_id, isbn_10) -> Union[Book, None]:
    book = (
        db.session.query(Book)
        .filter(Book.id == book_id)
        .update(
            {
                Book.isbn_10: isbn_10,
            }, synchronize_session=False))
    db.session.commit()
    return book


def update_book_isbn_13(
        book_id,
        isbn_13) -> Union[Book, None]:
    book = (
        db.session.query(Book)
        .filter(Book.id == book_id)
        .update(
            {
                Book.isbn_13: isbn_13,
            }, synchronize_session=False))
    db.session.commit()
    return book


def incr_instance_counter(book_id) -> Union[int, None]:
    """ Icrement book.instance_counter by 1.
    Return new value (int)"""
    book = Book.query.filter_by(id=book_id).first()
    if book:
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


def book_counter_created_by_user(
        user_id: int,
        days: int = 1) -> int:
    """ Returns how many Books created by User during last day """
    time_from = (datetime.today() - timedelta(days))
    _books = (db.session.query(Book.title)
              .filter(Book.created_by == user_id)
              .filter(Book.timestamp > time_from)
              .count())
    return _books

#  ------------  BOOK INSTANCE ------------------


def get_all_book_instances() -> List[BookInstance]:
    """ Returns all BookInstances with its owners and Book details """
    book_instances = (db.session.query(
        User.username,
        Book.title,
        Book.author,
        Book.isbn_10,
        Book.isbn_13,
        BookInstance.id,
        BookInstance.price,
        BookInstance.condition,
        BookInstance.description)
        .filter(BookInstance.owner_id == User.id)
        .filter(BookInstance.book_id == Book.id))
    return book_instances


def get_freshest_book_instances(items: int) -> List[BookInstance]:
    """ Returns n freshest BookInstances """
    book_instances = (db.session.query(
        User.username,
        User.latitude,
        User.longitude,
        BookInstance.book_id,
        Book.title,
        Book.author,
        Book.isbn_10,
        Book.isbn_13,
        BookInstance.id,
        BookInstance.price,
        BookInstance.condition,
        BookInstance.description,
        BookInstance.timestamp)
        .filter(BookInstance.owner_id == User.id)
        .filter(BookInstance.book_id == Book.id)
        .order_by(desc(BookInstance.timestamp)).limit(items).all())
    return book_instances


def create_book_instance(
        price,
        condition,
        description,
        owner_id,
        book_id) -> BookInstance:
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
        description) -> BookInstance:
    bi_prev_state = get_book_instance_by_id(book_instance_id)
    if (
        price != bi_prev_state.price
        or condition != bi_prev_state.condition
        or description != bi_prev_state.description
    ):
        bi = (
            db.session.query(BookInstance)
            .filter(BookInstance.id == book_instance_id)
            .update(
                {
                    BookInstance.price: price,
                    BookInstance.condition: condition,
                    BookInstance.description: description
                }, synchronize_session=False))
        db.session.commit()
        return bi
    return bi_prev_state


def delete_book_instance(book_instance_id: str) -> None:
    bi = get_book_instance_by_id(book_instance_id)
    decr_instance_counter(bi.book_id)
    BookInstance.query.filter_by(id=book_instance_id).delete()
    db.session.commit()


def get_book_instance_by_id(
        book_instance_id: str) -> Union[BookInstance, None]:
    """ Returns BookInstance object if exists in DB or None"""
    book_instance = (db.session.query(
        User.username,
        Book.title,
        Book.author,
        Book.isbn_10,
        Book.isbn_13,
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


def get_book_instances_by_user_id(user_id) -> List[BookInstance]:
    """ Returns list of BookInstance objects """
    book_instances = (db.session.query(
        User.username,
        User.id,
        Book.title,
        Book.author,
        Book.isbn_10,
        Book.isbn_13,
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


def get_book_instances_by_book_id(book_id) -> List[BookInstance]:
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


def get_expired_bi_with_users(expiration_period_days=30) -> List[BookInstance]:
    """ Returns user_email and bi_id & title & author for
    expired bi only."""
    expiration_time = datetime.today() - timedelta(days=expiration_period_days)
    expiration_time_timestamp = datetime.timestamp(expiration_time)

    book_instances = (db.session.query(
        User.email,
        BookInstance.id,
        Book.title,
        Book.author,
    )
        .filter(BookInstance.book_id == Book.id)
        .filter(BookInstance.is_active is True)
        .filter(BookInstance.timestamp <= expiration_time_timestamp)
        .filter(BookInstance.owner_id == User.id)
        .order_by(BookInstance.id.desc())
        .all())
    return book_instances


def deactivate_any_bi_if_expired(expiration_period_days=30) -> None:
    """ Update all b_instances status active -> inactive in DB if expired """
    # month_ago = now - 30 days
    expiration_time = datetime.today() - timedelta(days=expiration_period_days)
    expiration_time_timestamp = datetime.timestamp(expiration_time)
    (db.session.query(BookInstance)
     .filter(BookInstance.is_active is True)
     .filter(BookInstance.timestamp <= expiration_time_timestamp)
     .update({
         BookInstance.is_active: False,
     }, synchronize_session=False))
    db.session.commit()


def activate_book_instance(book_instance_id) -> None:
    (db.session.query(BookInstance)
     .filter(BookInstance.id == book_instance_id)
     .update({
         BookInstance.is_active: True,
         BookInstance.timestamp: datetime.utcnow()
     }, synchronize_session=False))
    db.session.commit()


def deactivate_book_instance(book_instance_id) -> None:
    (db.session.query(BookInstance)
     .filter(BookInstance.id == book_instance_id)
     .update({BookInstance.is_active: False}, synchronize_session=False))
    db.session.commit()


def get_active_bi_count(days: int = 0) -> int:
    ''' Returns quantity of active BookInstance objects created during last X days.
    if days == 0 --> count all active BookInstances.
    '''
    if days:
        time_from = (datetime.today() - timedelta(days))
        return (BookInstance.query
                .filter(BookInstance.timestamp > time_from)
                .filter(BookInstance.is_active == True)
                .count())
    return (BookInstance.query
            .filter(BookInstance.is_active == True)
            .count())

#  ------------ USER ------------------


def get_user_by_username(username: str) -> User:
    return User.query.filter_by(username=username).first_or_404()


def get_user_by_id(id: int) -> User:
    return User.query.filter_by(id=id).first_or_404()


def update_user_profile(
    about_me: str,
    latitude: str,
    longitude: str,
    username: str,
) -> User:
    """ Updates users coordinates, description at DB """
    user = (db.session.query(User)
            .filter(User.username == username)
            .update(
            {
                User.about_me: about_me,
                User.latitude: latitude,
                User.longitude: longitude,
            },
            synchronize_session=False,
            )
            )
    db.session.commit()
    return user


def create_user(username: str, email: str, avatar: str, latitude=50.4547,
                longitude=30.520) -> User:
    ''' Create new user '''

    user = User(
        username=username,
        email=email,
        avatar=avatar,
        latitude=latitude,
        longitude=longitude,
        about_me='you can contact me at @Telegram_my_acc',
        is_active=True
    )
    db.session.add(user)
    db.session.commit()
    return user


def delete_user(user_id) -> None:
    User.query.filter_by(id=user_id).delete()
    # TODO cascade delete all users book_instances???
    # Check if it generate any errors related to messages
    # (no recepient for exmpl)
    db.session.commit()


def get_count_active_users(days: int = 0) -> int:
    ''' Returns quantity of active Users during last X days.
    if days == 0 --> count all active Users.
    '''
    if days:
        time_from = (datetime.today() - timedelta(days))
        return (User.query
                .filter(User.last_seen > time_from)
                .count())
    return User.query.count()


#  ------------ MESSAGE ------------------

def get_message(message_id) -> Message:
    """ Returns Message object """
    message = Message.query.filter_by(id=message_id).first_or_404()
    return message


def get_messages_by_user(user_id) -> List[Message]:
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
