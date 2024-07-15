from pathlib import Path
from datetime import datetime
import xlsxwriter
from flask import Blueprint, request, render_template, redirect, session, jsonify, current_app
from election1.extensions import db
from election1.models import Classgrp, Office, Candidate, Tokenlist, Votes, Dates
from election1.vote.form import VotesForm, VoteForOne, VoteForMany
from election1.utils import get_token
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_

from sqlalchemy import asc
from election1.dclasses import CandidateDataClass
from typing import Dict, Any

vote = Blueprint('vote', __name__)


def office_grp_query(grp, office):
    return_list = []
    candidates = db.session.query(Candidate, Classgrp, Office).select_from(Candidate).join(Classgrp).join(
        Office).filter(and_(Office.office_title == office, Classgrp.name == grp))
    for c in candidates:
        return_list.append(tuple((c.Candidate.id_candidate, c.Candidate.firstname + " " + c.Candidate.lastname)))
        print(return_list)
    return return_list


@vote.route('/cast/<grp>/<token>', methods=['POST', 'GET'])
def cast(grp, token):
    # Check if there is a session then check the token

    if not session:
        print("Session is empty")
        token_list_record = get_tokenlist_record(token)
        if 'error' in token_list_record:
            home = current_app.config['HOME']
            return render_template('bad_token.html', error=token_list_record['error'], home=home)

        # token is OK

        print('no error')
        print(next(iter(token_list_record.items())))
        session['token_list_record'] = token_list_record
        print(token_list_record)

        print(grp)
        groups = grp.split('$')
        office_dict = get_office_dict(groups)
        session['office_dict_key'] = office_dict
        print(office_dict)

    # Get the office_dict from the session
    office_dict = session.get('office_dict_key', None)
    # find the next office to
    next_office = get_next_office(office_dict)
    print('y' + str(next_office))

    # if all the offices have been voted for then redirect to final check

    if next_office[2] == 1:  # vote for one
        print('vote for one')
        votes_form = VoteForOne()
        candidate_choices = office_grp_query(grp, next_office[0])
        VoteForOne.candidate.choices = candidate_choices
        return render_template('cast1.html', form=votes_form, office=next_office[0],
                               candidates=candidate_choices, grp=grp)

    if next_office[2] > 1:  # vote for one or more

        print('vote for one or more')
        votes_form = VoteForOne()
        candidate_choices = office_grp_query(grp, next_office[0])
        VoteForOne.candidate.choices = candidate_choices
        return render_template('cast2.html', form=votes_form, office=next_office[0],
                               candidates=candidate_choices, grp=grp, max_votes=next_office[2])

    return 'finished'


def vote_for_many(office, grp, max_votes):
    print('vote for one or more')
    candidate_choices = office_grp_query(grp, office)
    votes_form = VoteForMany()
    candidate_choices = office_grp_query(grp, office[0])
    VoteForOne.candidate.choices = candidate_choices
    return render_template('cast2.html', form=votes_form, office=office,
                           candidates=candidate_choices, grp=grp, max_votes=max_votes)


def get_office_dict(groups):
    office_dict = {}
    # office_dict2: Dict[str, Any] = {}
    # Query the database for all distinct groups
    # groups = db.session.query(Classgrp.name).distinct().all()

    # Initialize an empty dictionary

    # Loop through each group
    for group in groups:
        print(group)
        offices = query_offices_for_classgroup_with_details_as_list(group)
        print(offices)
        # Add the group and its associated offices to the dictionary
        # office_dict[group] = [[office[0], office[1], []] for office in offices]
        office_dict[group] = [[office[0], office[1], office[2], []] for office in offices]
        # for office in offices:
        #     office_dict[group] = [office, None, None]

    return office_dict


def query_offices_for_classgroup_with_details_as_list(classgroup_name):
    offices_query = db.session.query(
        Office.office_title,
        Office.sortkey,
        Office.office_vote_for
    ).join(Candidate).join(Classgrp).filter(
        Classgrp.name == classgroup_name
    ).distinct().order_by(Office.sortkey)

    offices = offices_query.all()

    return [[office.office_title, office.sortkey, office.office_vote_for] for office in offices]


@vote.route('/setup_tokens', methods=['POST', 'GET'])
def setup_tokens():
    Tokenlist.query.delete()

    p = Path(r"instance/voterTokens.xlsx")
    p.unlink(missing_ok=True)

    workbook = xlsxwriter.Workbook(r'instance\voterTokens.xlsx')
    worksheet = workbook.add_worksheet()

    row = 0
    col = 0

    while row < 101:
        token = get_token()
        try:
            new_tokenlist = Tokenlist(token=token,
                                      vote_submitted_date_time=None)
            db.session.add(new_tokenlist)
            db.session.commit()
            print('write ' + str(row))
        except SQLAlchemyError as e:
            db.session.rollback()
            print("except " + str(e))
            return redirect("/homepage")

        print(row)

        eclass = row % 4
        if eclass == 1:
            worksheet.write(row, col, 'http://127.0.0.1:5000/cast/Freshmen/' + token)
        elif eclass == 2:
            worksheet.write(row, col, 'http://127.0.0.1:5000/cast/Sophomore/' + token)
        elif eclass == 3:
            worksheet.write(row, col, 'http://127.0.0.1:5000/cast/Junior/' + token)
        elif eclass == 0:
            worksheet.write(row, col, 'http://127.0.0.1:5000/cast/Senior/' + token)

        row += 1

    workbook.close()

    print("did it")
    return render_template('mains.homepage')


def date_between():
    date = Dates.query.first()
    # Convert the epoch time to a datetime object
    start_date_time = datetime.fromtimestamp(date.start_date_time)
    end_date_time = datetime.fromtimestamp(date.end_date_time)

    # Get the current date time
    current_date_time = datetime.now()

    # Check if current date time is between start date time and end date time
    if start_date_time < current_date_time < end_date_time:
        return True
    else:
        return False


def get_tokenlist_record(token):
    """
    Retrieve a Tokenlist record if the given token exists in the Tokenlist.
    If the token does not exist, render a 'bad_token.html' template.

    :param token: The token to search for in the Tokenlist.
    :return: The Tokenlist record if the token exists, otherwise renders a template.
    """
    token_record = Tokenlist.query.filter_by(token=token).first()
    if token_record is None:
        # Token does not exist
        return {'error': 'Invalid token'}
    if token_record.vote_submitted_date_time is not None:
        # Token exists but vote has been submitted
        return {'error': 'Token has already been used'}

    # Token is valid and has not been used
    return token_record.to_dict()


def get_next_office(office_dict):
    """
    Get the next office from the office_dict.

    :param office_dict: A dictionary containing the group and its associated offices.
    :return: The next office from the office_dict.
    """
    for key, offices in office_dict.items():
        print(f"Key: {key}, Value: {offices}")
        for office in offices:
            print(f"Office: {office}")
            if not office[3]:
                return office
    return None
