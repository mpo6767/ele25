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


@vote.route('/cast/<grp_list>/<token>', methods=['POST', 'GET'])
def cast(grp_list, token):

    # Check if there is no session then check the validity of the token
    if not session:
        print("Session is empty log the token")
        token_list_record = get_tokenlist_record(token)
        if 'error' in token_list_record:
            print("log the token is bad")
            home = current_app.config['HOME']
            return render_template('bad_token.html', error=token_list_record['error'], home=home)

        print('log the token is good no error')
        print(next(iter(token_list_record.items())))
        session['token_list_record'] = token_list_record
        print(token_list_record)
        session['cnt'] = 0
        session['length'] = len(grp_list.split('$'))
        session['group'] = grp_list.split('$')[session.get('cnt')]
        grp = grp_list.split('$')[session.get('cnt')]
        print(grp)
        # groups = grp.split('$')
        office_dict = get_office_dict(grp_list.split('$'))

        session['office_dict'] = office_dict
        print(session.get('office_dict'))
        print('here office_dict')
        print(session.get('office_dict'))
        session['office_dict_length'] = len(session.get('office_dict'))
        session['current_office'] = 0

        # Get the office_dict from the session
        # office_dict = session.get('office_dict', None)

        next_office = get_next_office_for_group(session.get('office_dict'), session.get('group'))
        print('y' + str(next_office))

        session['office'] = next_office[0]
        if next_office[2] == 1:  # vote for one
            print('vote for one')
            votes_form = VoteForOne()
            candidate_choices = office_grp_query(grp, next_office[0])
            VoteForOne.candidate.choices = candidate_choices
            return render_template('cast1.html', form=votes_form, office=next_office[0],
                                   candidates=candidate_choices, grp=[session.get('group')])

        if next_office[2] > 1:  # vote for one or more

            print('vote for one or more')
            votes_form = VoteForMany()
            candidate_choices = office_grp_query(grp, next_office[0])
            VoteForMany.candidate.choices = candidate_choices
            return render_template('cast2.html', form=votes_form, office=next_office[0],
                                   candidates=candidate_choices, grp=[session.get('group')], max_votes=next_office[2])


    # if form_voteForeOne.validate_on_submit() and form_voteForeOne.submit.data:
    if request.method == 'POST':
        print(request.form.get('csrf_token'))
        print("POST")
        form_name = request.form.get('form_name')
        # if form_name == 'VoteForOne':
        #     print('VoteForOne')
        #     selected_candidate_id = request.form.get('candidate')
        # elif form_name == 'VoteForMany':
        #     checked_options = request.form.getlist('options')

        # office_dict = session.get('office_dict', {})

        group = session.get('group')
        office = session.get('office')

        print('group ' + str(group))
        print('office ' + str(office))
        print((session.get('office_dict')))
        if group in (session.get('office_dict')):
            for office_entry in session.get('office_dict')[group]:
                # Find the matching office
                if office_entry[0] == office:
                    if form_name == 'VoteForOne':
                        selected_candidate_id = request.form.get('candidate')
                        # Add the selected_candidate_id to the list of candidates voted for
                        print('log this ' + str(selected_candidate_id))
                        office_entry[3].append(selected_candidate_id)
                    elif form_name == 'VoteForMany':
                        selected_candidate_ids = request.form.getlist('candidates')
                        print(selected_candidate_ids)
                        # Add the checked_options to the list of candidates voted for
                        office_entry[3].extend(selected_candidate_ids)
                    break
            # Update the session with the modified office_dict
            # session['office_dict'] = office_dict
            print(session.get('office_dict'))

            next_office = get_next_office_for_group(session.get('office_dict'), session.get('group'))

            print('next_office ' + str(next_office))

            if next_office is None:
                print(session['cnt'])
                print(session['length'])
                if session['cnt'] + 1 < session['length']:
                    session['cnt'] += 1
                    session['group'] = grp_list.split('$')[session.get('cnt')]
                    next_office = get_next_office_for_group(session.get('office_dict'), session.get('group'))
                else:
                    print('no more offices')
                    return 'no more offices'
            
            session['office'] = next_office[0]
            if next_office[2] == 1:  # vote for one
                print('vote for one')
                print(next_office[0])
                votes_form = VoteForOne()
                grp = session.get('group', None)
                candidate_choices = office_grp_query(grp, next_office[0])
                VoteForOne.candidate.choices = candidate_choices
                return render_template('cast1.html', form=votes_form, office=next_office[0],
                                       candidates=candidate_choices, grp=grp)

            if next_office[2] > 1:  # vote for one or more

                print('vote for one or more')
                votes_form = VoteForMany()
                grp = session.get('group', None)
                candidate_choices = office_grp_query(grp, next_office[0])
                VoteForOne.candidate.choices = candidate_choices
                return render_template('cast2.html', form=votes_form, office=next_office[0],
                                       candidates=candidate_choices, grp=grp, max_votes=next_office[2])

    return 'no more offices'
def render_voting_form(form, office, candidates, grp, max_votes):
    """
    Renders the appropriate voting form template based on the type of vote.

    :param form: The form object to be used in the template.
    :param office: The office for which the vote is being cast.
    :param candidates: The list of candidates for the office.
    :param grp: The group/class of the voter.
    :param max_votes: The maximum number of votes allowed (for multiple votes). Default is 1 for single vote.
    :return: The rendered template response.
    """
    template_name = 'cast1.html' if max_votes == 1 else 'cast2.html'
    return render_template(template_name, form=form, office=office, candidates=candidates, grp=grp, max_votes=max_votes)


def get_office_dict(groups):
    office_dict = {}
    # Initialize an empty dictionary

    # Loop through each group and process the offices associated with the group
    for group in groups:
        print(group)
        offices = query_offices_for_classgroup_with_details_as_list(group)
        print(offices)
        # Add the group and its associated offices to the dictionary
        # office_dict[group] =
        # office{0] is the name of the office
        # office[1] is the sortkey
        # office[2] is the number of votes allowed
        # [] is the list of candidates voted for
        office_dict[group] = [[office[0], office[1], office[2], []] for office in offices]

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


def get_next_office_for_group(office_dict, group_name):
    """
    Get the next office for a specific group or return None if there are no more offices.

    :param office_dict: A dictionary containing groups and their associated offices.
    :param group_name: The specific group for which the next office is to be retrieved.
    :return: The next office for the group or None.
    """
    # Check if the group exists in the office_dict
    if group_name not in office_dict:
        return None

    # Iterate through the offices for the specified group
    for office in office_dict[group_name]:
        # Check if the list of candidates voted for is empty (office[3])
        if not office[3]:  # If empty, this is the next office to vote for
            return office
    # If all offices have been voted for, return None
    return None
