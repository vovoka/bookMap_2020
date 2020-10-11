import re

from flask import request
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms import (HiddenField, IntegerField, SelectField, StringField,
                     SubmitField, TextAreaField)
from wtforms.validators import (DataRequired, Length, NumberRange, Optional,
                                ValidationError)

from .models import User


class SearchForm(FlaskForm):
    q = StringField('Search', validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        if 'formdata' not in kwargs:
            kwargs['formdata'] = request.args
        if 'csrf_enabled' not in kwargs:
            kwargs['csrf_enabled'] = False
        super(SearchForm, self).__init__(*args, **kwargs)


def is_isbn_10(form, fieldname):
    _sum = 0
    isbn_val = form.data.get(fieldname)
    isbn = re.sub(r"[-–—\s]", "", isbn_val)
    checksum_passed = False
    if len(isbn) == 10:
        isbn = list(isbn)
        if isbn[-1] == "X" or isbn[-1] == "x":  # a final x stands for 10
            isbn[-1] = 10
        for d, i in enumerate(isbn[:-1]):
            _sum += (int(d) + 1) * int(i)
        checksum_passed = (_sum % 11) == int(isbn[-1])
    return checksum_passed


def is_isbn_13(form, fieldname):
    _sum = 0
    isbn_val = form.data.get(fieldname)
    isbn = re.sub(r"[-–—\s]", "", isbn_val)
    checksum_passed = False
    if len(isbn) == 13 and isbn[0:3] == "978" or "979":
        for d, i in enumerate(isbn):
            if int(d) % 2 == 0:
                _sum += int(i)
            else:
                _sum += int(i) * 3
        checksum_passed = _sum % 10 == 0
    return checksum_passed


def isbn_10_validator(form, field):
    if not is_isbn_10(form, 'isbn_10'):
        raise ValidationError('Sorry, is NOT a valid ISBN 10')
    return True


def isbn_13_validator(form, field):
    if not is_isbn_13(form, 'isbn_13'):
        raise ValidationError('Sorry, is NOT a valid ISBN 13')
    return True


def isbn_validator(form, field):
    if not (is_isbn_13(form, 'isbn') or is_isbn_10(form, 'isbn')):
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
    isbn_10 = StringField(
        'ISBN 10 (leave blank if no ISBN)',
        validators=[Optional(), isbn_10_validator]
    )
    isbn_13 = StringField(
        'ISBN 13 (leave blank if no ISBN)',
        validators=[Optional(), isbn_13_validator]
    )
    cover = FileField('Book cover', validators=[
        Optional(),
        FileAllowed(['jpg', 'jpeg'], '*.jpeg Images only!')
    ])
    submit = SubmitField('Add Book')


class AddBookByIsbnForm(FlaskForm):
    isbn = StringField(
        'Find book by ISBN',
        validators=[DataRequired(), isbn_validator]
    )
    submit = SubmitField('Try to find a book by ISBN')


class AddIsbnForm(FlaskForm):
    isbn_10 = StringField(
        'ISBN 10 (leave blank if no ISBN)',
        validators=[Optional(), isbn_10_validator]
    )
    isbn_13 = StringField(
        'ISBN 13 (leave blank if no ISBN)',
        validators=[Optional(), isbn_13_validator]
    )
    submit = SubmitField('Check book by ISBN')


class EditBookInstanceForm(FlaskForm):
    price = IntegerField(
        'My price, ₴',
        validators=[NumberRange(min=1, max=9999, message='Invalid price')]
    )
    condition = SelectField(
        'The book condition',
        choices=[
            ('4', 'Идеальное'),
            ('3', 'Хорошее (читана аккуратно, без пометок и заломов) '),
            ('2', 'Удовлетворительное'),
            ('1', 'Как есть (стоит уточннить нюансы с продавцом)')],
        validators=[DataRequired()]
    )
    description = StringField('Description')
    submit = SubmitField('Submit')


class MessageForm(FlaskForm):
    message = TextAreaField('Message', validators=[
        DataRequired(), Length(min=0, max=140)])
    submit = SubmitField('Submit')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Please use a different username.')


class EditProfileForm(FlaskForm):
    username = StringField('Username')
    about_me = TextAreaField('About me / alternative contact info', validators=[Length(min=0, max=140)])
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
