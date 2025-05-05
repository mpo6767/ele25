from flask_wtf import FlaskForm
from wtforms_alchemy import QuerySelectField

from election1.models import Classgrp, Office, Candidate
from wtforms import RadioField, SubmitField, BooleanField
from election1.extensions import db
from wtforms.validators import InputRequired


def classgrp_query():
    return Classgrp.query.order_by(Classgrp.sortkey)

class VoteForOne(FlaskForm):
    candidate = RadioField(label='candidate', choices=[], validators=[InputRequired()])
    submit = SubmitField(label='submit')


class VoteForMany(FlaskForm):
    def __init__(self, candidates=None, *args, **kwargs):
        super(VoteForMany, self).__init__(*args, **kwargs)
        if candidates:
            for candidate_id, candidate_name in candidates:
                setattr(self, f'candidate_{candidate_id}', BooleanField(label=candidate_name))
        self.submit = SubmitField('Submit')


class ReviewVotes(FlaskForm):
    submit = SubmitField(label='submit')

#
# class VoteRankChoice(FlaskForm):
#     candidate = RadioField(label='candidate', choices=[], validators=[InputRequired()])
#     submit = SubmitField(label='submit')


class  VoteResults(FlaskForm):
    choices_classgrp = QuerySelectField(label='class or group', query_factory=classgrp_query, get_label='name')
    submit = SubmitField(label='submit')

