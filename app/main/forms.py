from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from wtforms.validators import DataRequired, Length
from flask_wtf.file import FileField

from app.models import User


# class EditProfileForm(FlaskForm):
#     username = StringField('Username')
#     about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
#     latitude = StringField('Latitude', validators=[DataRequired()])
#     longitude = StringField('Longitude', validators=[DataRequired()])
#     submit = SubmitField('Submit')

#     def __init__(self, original_username, *args, **kwargs):
#         super(EditProfileForm, self).__init__(*args, **kwargs)
#         self.original_username = original_username

#     def validate_username(self, username):
#         if username.data != self.original_username:
#             user = User.query.filter_by(username=self.username.data).first()
#             if user is not None:
#                 raise ValidationError('Please use a different username.')


class AddBookForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    author = StringField('Author', validators=[DataRequired()])
    cover = FileField('Book cover')
    submit = SubmitField('Add Book')
    # TODO add validators


class BookInstanceForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    author = StringField('Author', validators=[DataRequired()])
    price = StringField('Price', validators=[DataRequired()])
    condition = StringField('Condition', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    cover = FileField('Book cover')
    submit = SubmitField('Submit')
