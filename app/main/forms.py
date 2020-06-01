from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange
from flask_wtf.file import FileField, FileAllowed


from flask import request


class SearchForm(FlaskForm):
    q = StringField('Search', validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        if 'formdata' not in kwargs:
            kwargs['formdata'] = request.args
        if 'csrf_enabled' not in kwargs:
            kwargs['csrf_enabled'] = False
        super(SearchForm, self).__init__(*args, **kwargs)


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
        )]
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
