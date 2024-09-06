from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField
from wtforms.validators import Length, DataRequired, ValidationError
from election1.models import Office


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

