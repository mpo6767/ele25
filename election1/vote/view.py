from pathlib import Path
from datetime import datetime
import xlsxwriter
import logging
from flask import Blueprint, request, render_template, redirect, session, current_app, url_for
from election1.extensions import db
from election1.models import Classgrp, Office, Candidate, Tokenlist, Votes, Dates
from election1.vote.form import VoteForOne, VoteForMany,ReviewVotes
from election1.utils import get_token
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_, func

vote = Blueprint('vote', __name__)

def log_vote_event(message):
    log_file = 'vote_view_log.txt'
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(log_file, 'a') as file:
        file.write(f"{timestamp} - {message}\n")

@vote.route('/cast/<grp_list>/<token>', methods=['POST', 'GET'])
def cast(grp_list, token):
    # if not date_between():
    #     home = current_app.config['HOME']
    #     return render_template('bad_date.html', home=home)

    # Check if there is no session then check the validity of the token
    if not session:
        token_list_record = get_tokenlist_record(token)
        if 'error' in token_list_record:
            log_vote_event(f"Token is bad: {token_list_record['error']} - Token: {token}")
            home = current_app.config['HOME']
            return render_template('bad_token.html', error=token_list_record['error'], home=home)
        log_vote_event(f"Token is good: {token}")
        '''
        I'm using session to store 
        the token_list_record, 
        the current group, 
        the office_dict, 
        the current office, 
        the current office_dict_length, 
        the current cnt, 
        and the current length
        '''
        session['token_list_record'] = token_list_record
        session['cnt'] = 0
        session['length'] = len(grp_list.split('$'))
        session['group'] = grp_list.split('$')[session.get('cnt')]
        grp = grp_list.split('$')[session.get('cnt')]
        office_dict = get_office_dict(grp_list.split('$'))

        session['office_dict'] = office_dict
        session['office_dict_length'] = len(session.get('office_dict'))
        session['current_office'] = 0

        # Get the office_dict from the session
        # office_dict = session.get('office_dict', None)

        next_office = get_next_office_for_group(session.get('office_dict'), session.get('group'))
        session['office'] = next_office[0]
        if next_office[2] == 1:  # vote for one
            print('vote for one')
            votes_form = VoteForOne()
            candidate_choices = office_grp_query(grp, next_office[0])
            VoteForOne.candidate.choices = candidate_choices
            return render_template('cast1.html', form=votes_form, office=next_office[0],
                                   candidates=candidate_choices, grp=[session.get('group')])

        if next_office[2] > 1:  # vote for one or
            votes_form = VoteForMany()
            candidate_choices = office_grp_query(grp, next_office[0])
            return render_template('cast2.html', form=votes_form, office=next_office[0],
                                   candidates=candidate_choices, grp=[session.get('group')], max_votes=next_office[2])

    # if form_voteForeOne.validate_on_submit() and form_voteForeOne.submit.data:
    if request.method == 'POST' or session.get('review', False):
        session['review'] = False
        form_name = request.form.get('form_name')
        if form_name == 'ReviewVotes':
            print('ReviewVotes')
            return 'ReviewVotes'

        group = session.get('group')
        office = session.get('office')

        if group in (session.get('office_dict')):
            for office_entry in session.get('office_dict')[group]:
                # Find the matching office
                if office_entry[0] == office:
                    if form_name == 'VoteForOne':
                        selected_candidate_id = request.form.get('candidate')
                        # Add the selected_candidate_id to the list of candidates voted for
                        print('log this ' + str(selected_candidate_id))
                        candidate_values = str(selected_candidate_id).split('$')
                        # office_entry[3].append(candidate_values[0])
                        office_entry[3].append([candidate_values[0], candidate_values[1]])
                        office_entry[4].append(candidate_values[1])
                    elif form_name == 'VoteForMany':
                        selected_candidate_ids = request.form.getlist('candidates')
                        print(selected_candidate_ids)
                        for candidate_id in selected_candidate_ids:
                            candidate_values = str(candidate_id).split('$')
                            office_entry[3].append([candidate_values[0], candidate_values[1]])
                            office_entry[4].append(candidate_values[1])
                        # Add the checked_options to the list of candidates voted for
                        # office_entry[3].extend(selected_candidate_ids)
                        break
            # Update the session with the modified office_dict
            # session['office_dict'] = office_dict
            next_office = get_next_office_for_group(session.get('office_dict'), session.get('group'))

            if next_office is None:
                if session['cnt'] + 1 < session['length']:
                    session['cnt'] += 1
                    session['group'] = grp_list.split('$')[session.get('cnt')]
                    next_office = get_next_office_for_group(session.get('office_dict'), session.get('group'))
                else:
                    print(session.get('office_dict'))
                    vote_form = ReviewVotes()
                    return render_template('cast3.html', form=vote_form, group=session.get('group'),
                                           office_dict=session.get('office_dict'))
            
            session['office'] = next_office[0]
            if next_office[2] == 1:  # vote for one
                votes_form = VoteForOne()
                grp = session.get('group', None)
                candidate_choices = office_grp_query(grp, next_office[0])
                return render_template('cast1.html', form=votes_form, office=next_office[0],
                                       candidates=candidate_choices, grp=grp)

            if next_office[2] > 1:  # vote for one or more
                votes_form = VoteForMany()
                grp = session.get('group', None)
                candidate_choices = office_grp_query(grp, next_office[0])
                VoteForOne.candidate.choices = candidate_choices
                return render_template('cast2.html', form=votes_form, office=next_office[0],
                                       candidates=candidate_choices, grp=grp, max_votes=next_office[2])
    vote_form = ReviewVotes()
    return render_template('cast3.html', form=vote_form, office=next_office[0],
                           office_dict=session.get('office_dict'))
    # return 'no more offices'


def office_grp_query(grp, office):
    return_list = []
    candidates = db.session.query(Candidate, Classgrp, Office).select_from(Candidate).join(Classgrp).join(
        Office).filter(and_(Office.office_title == office, Classgrp.name == grp))
    for c in candidates:
        return_list.append(tuple((c.Candidate.id_candidate, c.Candidate.firstname + " " + c.Candidate.lastname)))
    return return_list


def get_office_dict(groups):
    office_dict = {}
    # Initialize an empty dictionary

    # Loop through each group and process the offices associated with the group
    for group in groups:
        offices = query_offices_for_classgroup_with_details_as_list(group)
        # Add the group and its associated offices to the dictionary
        # office_dict[group] =
        # office{0] is the name of the office
        # office[1] is the sortkey
        # office[2] is the number of votes allowed
        # [] is the list of candidates voted for
        office_dict[group] = [[office[0], office[1], office[2], [], []] for office in offices]

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


@vote.route('/edit_choice/<office_id>/<group>', methods=['POST', 'GET'])
def edit_choice(office_id, group):
    office_dict = session.get('office_dict', {})

    if group in office_dict:
        for office in office_dict[group]:
            if office[1] == int(office_id):
                office[3] = []  # Clear the list of candidates voted for
                office[4] = []  # Clear the list of candidate names voted for
                break

    # Update the session with the modified office_dict
    session['office_dict'] = office_dict
    session['review'] = True
    # Redirect to the cast route with the current group and token
    token = session.get('token_list_record', {}).get('token', '')
    return redirect(url_for('vote.cast', grp_list=group, token=token))


@vote.route('/post_ballot', methods=['POST'])
def post_ballot():
    if request.method == 'POST':
        office_dict = session.get('office_dict', {})
        token = session.get('token_list_record', {}).get('token', '')
        # Process the submitted ballot data
        # (Add your logic here to handle the ballot submission)
        print("start")
        print(office_dict)
        for group in office_dict:
            print(office_dict[group])
            for office in office_dict[group]:
                print(office[3])
                for item in office[3]:
                    if item[0] != 99:
                        new_vote = Votes(id_candidate=item[0], votes_token=token)
                        db.session.add(new_vote)
                        log_vote_event(f"Vote submitted for candidate {item[0]} - {item[1]}")
                        pass
        try:
            token_record = Tokenlist.query.filter_by(token=token).first()
            if token_record:
                token_record.vote_submitted_date_time = datetime.now()
                db.session.commit()
            else:
                db.session.rollback()
                print("log the token does not exist")
                return "Error: Token record does not exist", 400
        except SQLAlchemyError as e:
            db.session.rollback()
            print(f"Database error: {e}")

        # Clear the session data related to the ballot
        session.clear()
        home = current_app.config['HOME']
        return render_template('thank_you.html', home=home)

'''
this is code to make the token list in an excel file
I suppose it could be in a different module but I placed it here just to save some time

the excel file is created in the instance folder and is a url to the cast route with the token as a parameter
'''
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


@vote.route('/vote_results', methods=['GET'])
def vote_results():
    results = db.session.query(
        Classgrp.name.label('group_name'),
        Office.office_title.label('office_title'),
        Candidate.firstname.label('candidate_firstname'),
        Candidate.lastname.label('candidate_lastname'),
        func.count(Votes.id_candidate).label('vote_total')
    ).join(Candidate, Votes.id_candidate == Candidate.id_candidate)\
     .join(Office, Candidate.id_office == Office.id_office)\
     .join(Classgrp, Candidate.id_classgrp == Classgrp.id_classgrp)\
     .group_by(Classgrp.name, Office.office_title, Candidate.firstname, Candidate.lastname)\
     .order_by(Classgrp.sortkey, Office.sortkey, func.count(Votes.id_candidate).desc())\
     .all()

    print(results)

    return render_template('vote_results.html', results=results)


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


