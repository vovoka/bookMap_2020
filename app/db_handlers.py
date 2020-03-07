from app import app
from app import db
from app.models import User, Book, BookInstance

#  ------------  BOOK ------------------ 

def create_book(title:str, author:str) -> object:
    if not book_exist(title, author):
        book = Book(title=title, author=author)
        db.session.add(book)
        db.session.commit()
        print('Book created "{title}" "{author}"', flush=True)
        return book


def book_exist(title:str, author:str) -> bool:
    """ Check if book with incoming attributes is in db """
    return bool(Book.query.filter_by(
        title=title,
        author=author
    ).first())


def get_book_id(title:str, author:str) -> int:
    """ Returns Book.id or None """
    book = Book.query.filter_by(
        title=title,
        author=author
    ).first()
    book_id = book.id if book else None
    return int(book_id)


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

def get_book_instance_by_id(book_instance_id:str) -> object:
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


#  ------------ USER ------------------ 