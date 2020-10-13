from .models import Book, BookInstance, User
from flask_admin import BaseView, expose
from .db_handlers import (
    obj_counter, get_active_bi_count, get_count_active_users)
from flask_admin.contrib.sqla import ModelView
from flask_admin.contrib.fileadmin import FileAdmin
import os.path as op
from . import admin, db


class AdminUserView(ModelView):
    ''' Used as a view wrapper in Flask-admin view. '''
    can_create = True
    page_size = 50  # the number of entries to display on the list view


class AnalyticsView(BaseView):
    @expose('/')
    def index(self):
        return self.render(
            'analytics_index.html',
            total_active_users=get_count_active_users(),  # all
            total_users=obj_counter(User),
            total_books=obj_counter(Book),
            total_bis=obj_counter(BookInstance),
            total_active_bis=get_active_bi_count(),
            month_active_users=get_count_active_users(30),  # month
            month_users=obj_counter(User, 30),
            month_books=obj_counter(Book, 30),
            month_bis=obj_counter(BookInstance, 30),
            month_active_bis=get_active_bi_count(30),
            week_active_users=get_count_active_users(7),  # week
            week_users=obj_counter(User, 7),
            week_books=obj_counter(Book, 7),
            week_bis=obj_counter(BookInstance, 7),
            week_active_bis=get_active_bi_count(7),
            day_active_users=get_count_active_users(1),  # day
            day_users=obj_counter(User, 1),
            day_books=obj_counter(Book, 1),
            day_bis=obj_counter(BookInstance, 1),
            day_active_bis=get_active_bi_count(1),
        )


def create_admin_views() -> None:
    """ Created all admin panel views """

    admin.add_view(AnalyticsView(name='Analytics', endpoint='analytics'))
    admin.add_view(AdminUserView(User, db.session, name='Users'))
    admin.add_view(AdminUserView(
        Book, db.session, name='Books'))
    admin.add_view(AdminUserView(
        BookInstance, db.session, name='BookInstances'))
    path = op.join(op.dirname(__file__), 'static')  # manage files
    admin.add_view(FileAdmin(path, '/static/', name='Files'))
