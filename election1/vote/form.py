from flask_wtf import FlaskForm
from election1.models import Classgrp, Office, Candidate
from wtforms import RadioField, SubmitField
from election1.extensions import db
from wtforms.validators import InputRequired
from election1.models import Tokenlist


def president_query():
    presidents = db.session.query(Candidate, Classgrp, Office).select_from(Candidate).join(Classgrp).join(
        Office).order_by(Classgrp.sortkey)
    return presidents


def vice_president_query():
    vice_presidents = db.session.query(Candidate, Classgrp, Office).select_from(Candidate).join(Classgrp).join(
        Office).order_by(Classgrp.sortkey)
    return vice_presidents


def secretary_query():
    secretarys = db.session.query(Candidate, Classgrp, Office).select_from(Candidate).join(Classgrp).join(
        Office).order_by(Office.sortkey).where(Classgrp.name == 'President')
    return secretarys


def treasurer_query():
    treasurers = db.session.query(Candidate, Classgrp, Office).select_from(Candidate).join(Classgrp).join(
        Office).order_by(Classgrp.sortkey)
    return treasurers


class VotesForm(FlaskForm):
    # def has_voted(self,token_to_check):
    #     result = db.session.query(Tokenlist).s
    #     tokenList = Tokenlist.query.filter_by(token=token_to_check).first()
    #     if tokenList.

    p_candidate = RadioField(label='president', choices=[], validators=[InputRequired()])
    vp_candidate = RadioField(label='vice_president', choices=[], validators=[InputRequired()])
    s_candidate = RadioField(label='secretary', choices=[], validators=[InputRequired()])
    t_candidate = RadioField(label='treasurer', choices=[], validators=[InputRequired()])
    submit = SubmitField(label='submit')
