from flask_wtf import FlaskForm
from wtforms import SubmitField, DateTimeLocalField
from wtforms.validators import InputRequired


class DatesForm(FlaskForm):
    start_date_time = DateTimeLocalField('Start Date', validators=[InputRequired()])
    end_date_time = DateTimeLocalField('End Date', validators=[InputRequired()])

    submit = SubmitField('Submit')