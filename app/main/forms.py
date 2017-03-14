from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length, Email, Regexp, ValidationError

from app.models import Role, User


class EditProfileForm(FlaskForm):
    name = StringField('your real name', validators=[Length(0, 64)])
    location = StringField('your location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')


class EditProfileAdminForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email(), Length(1, 64)])
    username = StringField('Username', validators=[
        DataRequired(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                              'Username can only have letters, numbers, dots '
                                              'or underscores, and start with letters.')])
    confirmed = BooleanField('confirmed')
    role = SelectField('role', coerce=int)
    name = StringField('name', validators=[Length(0, 64)])
    location = StringField('location', validators=[Length(0, 64)])
    about_me = TextAreaField('about_me')
    submit = SubmitField('Submit')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name) for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.email and User.query.filter_by(email=field.data).first():
            raise ValidationError('email have been registered')

    def validate_username(self, field):
        if field.data != self.user.username and User.query.filter_by(username=field.data).first():
            raise ValidationError('username has been registered')


class PostForm(FlaskForm):
    body = TextAreaField("what's on your mind?", validators=[DataRequired()])
    submit = SubmitField('Submit')
