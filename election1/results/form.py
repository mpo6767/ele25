from flask_wtf import FlaskForm
from wtforms_alchemy import QuerySelectField
from wtforms import SubmitField
from election1.models import Classgrp


class  VoteResults(FlaskForm):
    choices_classgrp = QuerySelectField(label='class or group', query_factory=Classgrp.classgrp_query, get_label='name')
    submit = SubmitField(label='submit')

