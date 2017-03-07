from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class NameForm(FlaskForm):
    name = StringField('please input your name', validators=[DataRequired()])
    submit = SubmitField('Submit')
