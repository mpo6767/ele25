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
    choices_classgrp = SelectField('class', choices=[], validators=[Length(min=2, max=30), DataRequired()])
    choices_office = QuerySelectField(query_factory=office_query, label='office title', get_label='office_title')
    submit = SubmitField(label='submit')


class Candidate_reportForm(FlaskForm):
    choices_classgrp = QuerySelectField(label='class or group', query_factory=classgrp_query, get_label='name')
    choices_office = QuerySelectField(query_factory=office_query, label='office title', get_label='office_title')
    submit = SubmitField(label='submit')


class OfficeForm(FlaskForm):
    @staticmethod
    def validate_office_title(form, field):
        title = Office.query.filter_by(office_title=field.data).first()
        if title:
            raise ValidationError('Office must be unique')

    @staticmethod
    def validate_sortkey(form, field):
        classgrp = Office.query.filter_by(sortkey=field.data).first()
        if classgrp:
            raise ValidationError('This sort key already exists in the database.')

    office_title = StringField(label='Office Title . . .', validators=[Length(min=2, max=30), DataRequired()])
    office_vote_for = IntegerField(label='Vote For . . .', default=1)
    sortkey = IntegerField(label='Sort Key . . .', default=None, validators=[DataRequired()])
    submit = SubmitField(label='submit')


class ClassgrpForm(FlaskForm):

    name = StringField(label='Class or Group . . .', validators=[Length(min=2, max=30), DataRequired()])
    sortkey = IntegerField(label='Sort Key . . .', validators=[DataRequired()])
    submit = SubmitField(label='submit')

    @staticmethod
    def validate_name(form, field):
        classgrp = Classgrp.query.filter_by(name=field.data).first()
        if classgrp:
            raise ValidationError('This class or group name already exists in the database.')
    @staticmethod
    def validate_sortkey(form, field):
        classgrp = Classgrp.query.filter_by(sortkey=field.data).first()
        if classgrp:
            raise ValidationError('This sort key already exists in the database.')
class DatesForm(FlaskForm):
    start_date_time = DateTimeLocalField('Start Date', validators=[InputRequired()])
    end_date_time = DateTimeLocalField('End Date', validators=[InputRequired()])

    submit = SubmitField('Submit')
