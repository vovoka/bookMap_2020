#!/usr/bin/env python
from datetime import datetime, timedelta
import unittest
from app import app, db
from app.models import User, Book
from app.db_handlers import (get_book_id, book_exist,
                             get_books_by_user_id)


class UserModelCase(unittest.TestCase):
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_password_hashing(self):
        u = User(username='susan')
        u.set_password('cat')
        self.assertFalse(u.check_password('dog'))
        self.assertTrue(u.check_password('cat'))

    def test_avatar(self):
        u = User(username='john', email='john@example.com')
        self.assertEqual(u.avatar(128), ('https://www.gravatar.com/avatar/'
                                         'd4c74594d841139328695756648b6bd6'
                                         '?d=identicon&s=128'))


class BookModelCase(unittest.TestCase):
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        db.create_all()
        # create 2 books
        book_1 = Book(title='test_title', author='test_author')
        db.session.add(book_1)
        book_2 = Book(title='test_title_2', author='test_author_2')
        db.session.add(book_2)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_get_book_id(self):
        self.assertEqual(get_book_id('test_title', 'test_author'), 1)
        self.assertEqual(get_book_id('test_title_00', 'test_author'), None)
        self.assertEqual(get_book_id('', ''), None)

    def test_book_exist(self):
        self.assertEqual(book_exist(title='test_title',
                                    author='test_author'), True)
        self.assertEqual(book_exist(title='test_title_not',
                                    author='test_author'), False)
        self.assertEqual(book_exist('', ''), False)

    # def test_get_books_by_user_id(self):
    #     # create_user (to not get error with book.owner_id
    #     u1 = User(username='john', email='john@example.com')
    #     db.session.add(u1)
    #     db.session.commit()

    #     book = Book(title='test_title', author='test_author')
    #     db.session.add(book)
    #     db.session.commit()

    #     book = Book(title='test_title_2', author='test_author')
    #     db.session.add(book)
    #     db.session.commit()

    #     books = get_books_by_user_id('1')
    #     books_ids = [book.id for book in books]
    #     for book in books:
    #         print(book.id, flush=True)
    #     self.assertEqual(list(books_ids), [1, 2])


    # def test_follow(self):
    #     u1 = User(username='john', email='john@example.com')
    #     u2 = User(username='susan', email='susan@example.com')
    #     db.session.add(u1)
    #     db.session.add(u2)
    #     db.session.commit()
    #     self.assertEqual(u1.followed.all(), [])
    #     self.assertEqual(u1.followers.all(), [])

    #     u1.follow(u2)
    #     db.session.commit()
    #     self.assertTrue(u1.is_following(u2))
    #     self.assertEqual(u1.followed.count(), 1)
    #     self.assertEqual(u1.followed.first().username, 'susan')
    #     self.assertEqual(u2.followers.count(), 1)
    #     self.assertEqual(u2.followers.first().username, 'john')

    #     u1.unfollow(u2)
    #     db.session.commit()
    #     self.assertFalse(u1.is_following(u2))
    #     self.assertEqual(u1.followed.count(), 0)
    #     self.assertEqual(u2.followers.count(), 0)

    # def test_follow_posts(self):
    #     # create four users
    #     u1 = User(username='john', email='john@example.com')
    #     u2 = User(username='susan', email='susan@example.com')
    #     u3 = User(username='mary', email='mary@example.com')
    #     u4 = User(username='david', email='david@example.com')
    #     db.session.add_all([u1, u2, u3, u4])

    #     # create four posts
    #     now = datetime.utcnow()
    #     p1 = Post(body="post from john", author=u1,
    #               timestamp=now + timedelta(seconds=1))
    #     p2 = Post(body="post from susan", author=u2,
    #               timestamp=now + timedelta(seconds=4))
    #     p3 = Post(body="post from mary", author=u3,
    #               timestamp=now + timedelta(seconds=3))
    #     p4 = Post(body="post from david", author=u4,
    #               timestamp=now + timedelta(seconds=2))
    #     db.session.add_all([p1, p2, p3, p4])
    #     db.session.commit()

    #     # setup the followers
    #     u1.follow(u2)  # john follows susan
    #     u1.follow(u4)  # john follows david
    #     u2.follow(u3)  # susan follows mary
    #     u3.follow(u4)  # mary follows david
    #     db.session.commit()

    #     # check the followed posts of each user
    #     f1 = u1.followed_posts().all()
    #     f2 = u2.followed_posts().all()
    #     f3 = u3.followed_posts().all()
    #     f4 = u4.followed_posts().all()
    #     self.assertEqual(f1, [p2, p4, p1])
    #     self.assertEqual(f2, [p2, p3])
    #     self.assertEqual(f3, [p3, p4])
    #     self.assertEqual(f4, [p4])


if __name__ == '__main__':
    unittest.main(verbosity=2)
