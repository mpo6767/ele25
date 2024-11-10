from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, DateTimeLocalField, SelectField
from wtforms.validators import Length, DataRequired, ValidationError, InputRequired
from election1.models import Classgrp, Office
from wtforms_alchemy.fields import QuerySelectField


def classgrp_query():
    return Classgrp.query.order_by(Classgrp.sortkey)


def office_query():
    return Office.query.order_by(Office.sortkey)

class CandidateForm(FlaskForm):
    firstname = StringField(label='firstname', validators=[Length(min=2, max=30), InputRequired()])
    lastname = StringField(label='lastname', validators=[Length(min=2, max=30), DataRequired()])
    choices_classgrp = SelectField('class/group', choices=[], validators=[Length(min=2, max=30), DataRequired()])
    choices_office = SelectField('office title', choices=[], validators=[Length(min=2, max=30), DataRequired()])
    submit = SubmitField(label='submit')


class Candidate_reportForm(FlaskForm):
    choices_classgrp = QuerySelectField(label='class or group', query_factory=classgrp_query, get_label='name')
    choices_office = QuerySelectField(query_factory=office_query, label='office title', get_label='office_title')
    submit = SubmitField(label='submit')


class WriteinCandidateForm(FlaskForm):
    choices_classgrp = QuerySelectField(label='class or group', query_factory=classgrp_query, get_label='name')
    choices_office = QuerySelectField(query_factory=office_query, label='office title', get_label='office_title')
    writein_candidate_name = StringField(label='write-in candidate name', validators=[Length(min=6, max=45), DataRequired()])
    submit = SubmitField(label='submit')

