from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, DateTimeLocalField
from wtforms.validators import Length, EqualTo, Email, DataRequired, ValidationError,InputRequired
from election1.models import Classgrp, Office
from wtforms_alchemy.fields import QuerySelectField
from datetime import datetime



def classgrp_query():
    return Classgrp.query.order_by(Classgrp.sortkey)

def office_query():
    return Office.query.order_by(Office.sortkey)


class CandidateForm(FlaskForm):
    firstname = StringField(label='firstname', validators=[Length(min=2, max=30), InputRequired()])
    lastname = StringField(label='lastname', validators=[Length(min=2, max=30), DataRequired()])
    choices_classgrp = QuerySelectField(label='class or group', query_factory=classgrp_query,  get_label='name')
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
    def validate_sortkey(self, office_sortkey_to_check):
        sortkey = Office.query.filter_by(sortkey=office_sortkey_to_check.data).first()
        if sortkey:
            raise ValidationError('Sort key must be unique')

    office_title = StringField(label='Office Title . . .', validators=[Length(min=2, max=30), DataRequired()])
    office_vote_for = IntegerField(label='Vote For . . .', default=1)
    sortkey = IntegerField(label='Sort Key . . .', validators=[DataRequired()])
    submit = SubmitField(label='submit')

class ClassgrpForm(FlaskForm):
    def validate_name(self, name_to_check):
        name = Classgrp.query.filter_by(name=name_to_check.data).first()
        if name:
            raise ValidationError('Class or Group must be unique')
    def validate_sortkey(self, sortkey_to_check):
        sortkey = Classgrp.query.filter_by(sortkey=sortkey_to_check.data).first()
        if sortkey:
            raise ValidationError('Sort key must be unique')
    name = StringField(label='Class or Group . . .', validators=[Length(min=2, max=30), DataRequired()])
    sortkey = IntegerField(label='Sort Key . . .', validators=[DataRequired()])
    submit = SubmitField(label='submit')

class DatesForm(FlaskForm):
    start_date_time = DateTimeLocalField('Start Date',validators=[InputRequired()])
    end_date_time = DateTimeLocalField('End Date',validators=[InputRequired()])

    submit = SubmitField('Submit')