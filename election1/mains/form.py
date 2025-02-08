from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField,  BooleanField
from wtforms.validators import Length, InputRequired


class LoginForm(FlaskForm):
    login_so_name = StringField(label='username', validators=[Length(min=2, max=30), InputRequired()])
    login_pass = PasswordField(label='password', validators=[Length(min=2, max=30), InputRequired()])
    remember = BooleanField(label='remember me')
    submit = SubmitField(label='submit')