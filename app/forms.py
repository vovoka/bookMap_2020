from app.models import User
from wtforms.validators import ValidationError, DataRequired, Email, Length, InputRequired, NumberRange
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, IntegerField, HiddenField, SelectField
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from app import db_handlers

from flask import request
import re


class SearchForm(FlaskForm):
    q = StringField('Search', validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        if 'formdata' not in kwargs:
            kwargs['formdata'] = request.args
        if 'csrf_enabled' not in kwargs:
            kwargs['csrf_enabled'] = False
        super(SearchForm, self).__init__(*args, **kwargs)


def isbn_is_not_exist(form, field):
    book = db_handlers.get_book_by_isbn(field.data)
    if book:
        raise ValidationError(f'Book with isbn {field.data} already exist in database:\
             {book.title} by {book.author}. Please, do not create duplicates, use search.')


def is_isbn(form, fieldname):
    sum = 0
    isbn = form.data.get(fieldname)
    isbn = re.sub(r"[-–—\s]", "", isbn)

    # isbn13
    # is it a ISBN? Thanks @librarythingtim
    if len(isbn) == 13 and isbn[0:3] == "978" or "979":
        for d, i in enumerate(isbn):
            # if (int(d) + 1) % 2 != 0:
            if int(d) % 2 == 0:
                sum += int(i)
            else:
                sum += int(i) * 3
        return sum % 10 == 0

    # isbn10
    if len(isbn) == 10:
        isbn = list(isbn)
        if isbn[-1] == "X" or isbn[-1] == "x":  # a final x stands for 10
            isbn[-1] = 10
        for d, i in enumerate(isbn[:-1]):
            sum += (int(d)+1) * int(i)
        return (sum % 11) == int(isbn[-1])

    return False


def is_valid_isbn(form, field):
    if not is_isbn(form, 'isbn'):
        raise ValidationError('Sorry, is NOT a valid ISBN')
    return True


class AddBookForm(FlaskForm):
    title = StringField(
        'Title',
        validators=[DataRequired(), Length(min=1, max=140, message='Too long')]
    )
    author = StringField(
        'Author',
        validators=[DataRequired(), Length(min=1, max=140, message='Too long')]
    )
    isbn = StringField(
        'ISBN (leave blank if no ISBN)',
        validators=[is_valid_isbn or None]
    )
    cover = FileField('Book cover', validators=[
        DataRequired(),
        FileAllowed(['jpg', 'jpeg'], '*.jpeg Images only!')
    ])
    submit = SubmitField('Add Book')


class AddIsbnForm(FlaskForm):
    isbn = StringField(
        'ISBN',
        validators=[is_valid_isbn]
    )
    submit = SubmitField('Add ISBN')


class EditBookInstanceForm(FlaskForm):
    price = IntegerField(
        'Price',
        validators=[NumberRange(min=1, max=9999, message='Invalid price')]
    )
    condition = SelectField(
        'The book instance condition',
        choices=[
            ('4', 'Идеальное'),
            ('3', 'Хорошее (читана аккуратно, без пометок и заломов) '),
            ('2', 'Удовлетворительное'),
            ('1', 'Как есть (стоит уточннить нюансы с продавцом)')],
        validators=[DataRequired()]
    )
    description = StringField('Description', validators=[DataRequired()])
    submit = SubmitField('Submit')


class MessageForm(FlaskForm):
    message = TextAreaField('Message', validators=[
        DataRequired(), Length(min=0, max=140)])
    submit = SubmitField('Submit')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


class EditProfileForm(FlaskForm):
    username = StringField('Username')
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
    latitude = HiddenField('Latitude', validators=[DataRequired()])
    longitude = HiddenField('Longitude', validators=[DataRequired()])
    submit = SubmitField('Submit')

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Please use a different username.')
