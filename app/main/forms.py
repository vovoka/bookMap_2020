from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, TextAreaField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Length, NumberRange
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
