from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email, Regexp, equal_to, ValidationError

from app.models import User


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('remember me')
    submit = SubmitField('Submit')


class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64), Email()])
    username = StringField('Username', validators=[
        DataRequired(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                              'Username can only have letters, numbers, dots '
                                              'or underscores, and start with letters.')])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Confirm password', validators=[
        DataRequired(), equal_to('password', message='password must match.')])
    submit = SubmitField('Submit')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('email already exist.')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('username has been registered')


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('old_password', validators=[DataRequired()])
    new_password = PasswordField('new_password', validators=[DataRequired()])
    new_password2 = PasswordField('confirm password', validators=[
        DataRequired(), equal_to('new_password', 'password not match')])
    submit = SubmitField('Submit')

    def validate_old_password(self, field):
        if current_user.verify_password(field.data) is False:
            raise ValidationError('wrong password')


class ForgetPassword(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64), Email()])
    submit = SubmitField('Submit')


class ResetPassword(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64), Email()])
    new_password = PasswordField('new password', validators=[DataRequired()])
    new_password2 = PasswordField('confirm password', validators=[
        DataRequired(), equal_to('new_password', 'password not match')])
    submit = SubmitField('Submit')


class ChangeEmail(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField('password', validators=[DataRequired()])
    submit = SubmitField('Submit')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email has been registered')

