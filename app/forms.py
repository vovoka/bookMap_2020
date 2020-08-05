from app.models import User
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length, NumberRange
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, IntegerField, HiddenField
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from app import db_handlers

from flask import request


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


class AddBookForm(FlaskForm):
    title = StringField(
        'Title',
        validators=[DataRequired(), Length(min=1, max=140, message='Too long')]
    )
    author = StringField(
        'Author',
        validators=[DataRequired(), Length(min=1, max=140, message='Too long')]
    )
    isbn = IntegerField(
        'isbn',
        validators=[NumberRange(
            min=0,
            max=99999999999999,
            message='isbn is out of range'
        ),
            isbn_is_not_exist
        ]
    )
    cover = FileField('Book cover', validators=[
        DataRequired(),
        FileAllowed(['jpg', 'jpeg'], '*.jpeg Images only!')
    ])
    submit = SubmitField('Add Book')


class BookInstanceForm(FlaskForm):
    title = StringField(
        'Title',
        validators=[DataRequired(), Length(min=1, max=140, message='Too long')]
    )
    author = StringField(
        'Author',
        validators=[DataRequired(), Length(min=1, max=140, message='Too long')]
    )
    isbn = IntegerField(
        'isbn',
        validators=[NumberRange(
            min=0,
            max=99999999999999,
            message='isbn is out of range'
        )]
    )
    price = IntegerField('Price', validators=[DataRequired()])
    condition = StringField('Condition', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    cover = FileField('Book cover', validators=[
        DataRequired(),
        FileAllowed(['jpg', 'jpeg'], '*.jpeg Images only!')
    ])
    submit = SubmitField('Submit')


class EditBookInstanceForm(FlaskForm):
    price = IntegerField('Price', validators=[DataRequired()])
    condition = StringField('Condition', validators=[DataRequired()])
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
