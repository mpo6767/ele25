from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, EmailField
from wtforms.validators import Length, EqualTo, Email, DataRequired, ValidationError,InputRequired
from wtforms_alchemy.fields import QuerySelectField
from election1.models import Classgrp, Office
# from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user


def classgrp_query():
    return Classgrp.query

def office_query():
    return Office.query


class CandidateForm(FlaskForm):
    firstname = StringField(label='firstname', validators=[Length(min=2, max=30), InputRequired()])
    lastname = StringField(label='lastname', validators=[Length(min=2, max=30), DataRequired()])
    choices_classgrp = QuerySelectField(label='class or group',query_factory=classgrp_query,  get_label='name')
    choices_office = QuerySelectField(query_factory=office_query, label='office title', get_label='office_title')
    submit = SubmitField(label='submit')

class Candidate_reportForm(FlaskForm):
    choices_classgrp = QuerySelectField(label='class or group',query_factory=classgrp_query,  get_label='name')
    choices_office = QuerySelectField(query_factory=office_query, label='office title', get_label='office_title')
    submit = SubmitField(label='submit')

class OfficeForm(FlaskForm):
    def validate_office_title(self, office_title_to_check):
        title = Office.query.filter_by(office_title=office_title_to_check.data).first()
        if title:
            raise ValidationError('Office must be unique')

    office_title = StringField(label='Office Title . . .',validators=[Length(min=2, max=30), DataRequired()])
    sortkey = IntegerField(label='Sort Key . . .', validators=[DataRequired()])
    submit = SubmitField(label='submit')

class ClassgrpForm(FlaskForm):
    def validate_name(self, name_to_check):
        name = Classgrp.query.filter_by(name=name_to_check.data).first()
        if name:
            raise ValidationError('Class or Group must be unique')
    name = StringField(label='Class or Group . . .', validators=[Length(min=2, max=30), DataRequired()])
    sortkey = IntegerField(label='Sort Key . . .', validators=[DataRequired()])
    submit = SubmitField(label='submit')

class UserForm(FlaskForm):
    user_firstname = StringField(label='firstname', validators=[Length(min=2, max=30), InputRequired()])
    user_lastname = StringField(label='lastname', validators=[Length(min=2, max=30), InputRequired()])
    user_so_name = StringField(label='user name', validators=[Length(min=2, max=30), InputRequired()])
    user_pass = StringField(label='password', validators=[Length(min=2, max=30), InputRequired()])
    user_role = StringField(label='role', validators=[Length(min=1, max=1), InputRequired()])
    user_email = EmailField(label='email', validators=[Email()])
    submit = SubmitField(label='submit')


class LoginForm(FlaskForm):
    login_so_name = StringField(label='username', validators=[Length(min=2, max=30), InputRequired()])
    login_pass = PasswordField(label='password', validators=[Length(min=2, max=30), InputRequired(),
                                                            EqualTo('user_pass2', message='passwords must match')])
    submit = SubmitField(label='submit')


# class ChangePW(FlaskForm):
#     user_pass = PasswordField(label='password', validators=[Length(min=2, max=30), InputRequired(), EqualTo('user_pass2', message='passwords must match')])
#     user_pass2 = PasswordField(label='pw check', validators=[Length(min=2, max=30), InputRequired()])Lo
#     submit = SubmitField(label='submit')
