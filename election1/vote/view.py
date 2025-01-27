from datetime import datetime
from flask import Blueprint, request, render_template, redirect, session, current_app, url_for, flash
from election1.extensions import db
from election1.models import Classgrp, Office, Candidate, Tokenlist, Votes, Dates
from election1.vote.form import VoteForOne, VoteForMany, ReviewVotes, VoteResults
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_, func, null
from election1.dclasses import CandidateDataClass
from collections import defaultdict

vote = Blueprint('vote', __name__)


class CandidateDataClassSingleton:
    _instance = None
    _candidates = []

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CandidateDataClassSingleton, cls).__new__(cls)
        return cls._instance

    def set_candidates(self, candidates: list[CandidateDataClass]):
        self._candidates = candidates

    def get_candidates(self) -> list[CandidateDataClass]:
        return self._candidates


def log_vote_event(message):
    log_file = 'vote_view_log.txt'
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(log_file, 'a') as file:
        file.write(f"{timestamp} - {message}\n")


@vote.route('/group/search')
def group_search():
    group = request.args.get('choices_classgrp', type=int)
    candidates = db.session.query(Candidate, Classgrp, Office).select_from(Candidate).join(Classgrp).join(
        Office).order_by(Classgrp.sortkey, Office.sortkey).where(Classgrp.id_classgrp == group)
    return render_template('vote_results.html',  candidates=candidates)


@vote.route('/cast/<grp_list>/<token>', methods=['POST', 'GET'])
def cast(grp_list, token):
    log_vote_event('+++ cast '
                   f"grp_list: {grp_list}, token: {token}, ")

    # if not date_between():
    #     home = current_app.config['HOME']
    #     return render_template('bad_date.html', home=home)

    # Check if there is no session then check the validity of the token
    global next_office
    if not session:
        log_vote_event('new session' 
                       f' for grp_list: {grp_list}, and token: {token}, ')


    # validate the groups are valid - its a double check on the url presented
        if not are_all_classgrps_valid(grp_list):
            log_vote_event(f"Invalid class group: {grp_list}")
            home = current_app.config['HOME']
            error = 'Invalid class group ' + grp_list
            return render_template('bad_token.html', error=error, home=home)

    # token list is a record  (row) of the model Tokenlist the  Tokenlist is a dictionary of column: values

        token_list_record =Tokenlist. get_tokenlist_record(token)
        if token_list_record.get('grp_list') == grp_list:
            log_vote_event(f"grp_list matches the value in token_list_record: {grp_list} - Token: {token}")

        if 'error' in token_list_record:
            log_vote_event(f"Token is bad: {token_list_record['error']} - Token: {token}")
            home = current_app.config['HOME']
            return render_template('bad_token.html', error=token_list_record['error'], home=home)

        # the token seems good so log the event.   This does not mean that the voter has voted
        log_vote_event(f"Token is good: {token}")

        '''
        I'm using session to store 
        the token_list_record, 
        the current group, 
        the office_dict, 
        the current office, 
        the current office_dict_length, 
        the cnt = current group number
        and the  length = nbr of groups
        '''
        log_vote_event('token_list_record ' + str(token_list_record))
        session['token_list_record'] = token_list_record
        # in a school election the groups are the classes at a minimum
        # the cnt is the current group number there maybe more than 1 group
        session['cnt'] = 0 # is the setup for the first group or only group in the list
        log_vote_event('grp_list ' + grp_list)

        # nbr of groups are seperated by $ in the url
        session['length'] = len(grp_list.split('$'))
        # since there could be more than 1 group for the voter the group in
        # in session is the current group used to get the offices
        # the group_list is iterated through to get the next group
        session['group'] = grp_list.split('$')[session.get('cnt')]
        session['grp_list'] = grp_list
        grp = grp_list.split('$')[session.get('cnt')]

        # get the office_dict from the database for the group
        # office_dict = get_office_dict(grp_list.split('$'))
        office_dict = {}

        for group in (grp_list.split('$')):
            offices =Office. query_offices_for_classgroup_with_details_as_list(group)
            # Add the group and its associated offices to the dictionary
            # office_dict[group] =
            # office{0] is the name of the office
            # office[1] is the sortkey
            # office[2] is the number of votes allowed
            # [] is the list of candidates voted for
            log_vote_event('offices ' + str(offices))
            office_dict[group] = [[office[0], office[1], office[2], [], []] for office in offices]
            log_vote_event(' ++  office_dict ' + str(office_dict))


        session['office_dict'] = office_dict
        print('office_dict ' + str(session.get('office_dict')))
        session['office_dict_length'] = len(session.get('office_dict'))
        session['current_office'] = 0

        # Get the office_dict from the session
        # office_dict = session.get('office_dict', None)

        next_office = get_next_office_for_group(session.get('office_dict'), session.get('group'))
        if next_office is None:
            if session['cnt'] + 1 < session['length']:
                session['cnt'] += 1
                session['group'] = grp_list.split('$')[session.get('cnt')]
                next_office = get_next_office_for_group(session.get('office_dict'), session.get('group'))

            else:

                vote_form = ReviewVotes()
                return render_template('cast3.html', form=vote_form, grp=grp,
                                       office_dict=session.get('office_dict'))

        session['office'] = next_office[0]
        if next_office[2] == 1:  # vote for one

            votes_form = VoteForOne()
            candidate_choices = office_grp_query(grp, next_office[0])
            print('candidate_choices ' + str(candidate_choices))
            writein_candidate_id = has_writein_candidate(candidate_choices)
            html_writein = 0
            if writein_candidate_id is not None:
                html_writein = writein_candidate_id
                filtered_choices = remove_writein_candidate(candidate_choices, writein_candidate_id)
                VoteForOne.candidate.choices = filtered_choices
            else:
                # html_writein = 0
                VoteForOne.candidate.choices = candidate_choices
            print ('VoteForOne.candidate.choices ' + str(VoteForOne.candidate.choices))
            return render_template('cast1.html', form=votes_form, office=next_office[0],
                                   candidates=VoteForOne.candidate.choices, grp=grp, html_writein=html_writein)

        if next_office[2] > 1:  # vote for one or
            votes_form = VoteForMany()
            candidate_choices = office_grp_query(grp, next_office[0])
            return render_template('cast2.html', form=votes_form, office=next_office[0],
                                   candidates=candidate_choices, grp=grp, max_votes=next_office[2])

    # if form_voteForeOne.validate_on_submit() and form_voteForeOne.submit.data:
    log_vote_event('167 ')
    log_vote_event('check request.method ' + request.method)
    if request.method == 'POST' or session.get('review', False):
        session['review'] = False
        form_name = request.form.get('form_name')
        if form_name == 'ReviewVotes':
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
                        log_vote_event('log this non final ' + str(selected_candidate_id))
                        candidate_values = str(selected_candidate_id).split('$')
                        # office_entry[3].append(candidate_values[0])
                        office_entry[3].append([candidate_values[0], candidate_values[1]])
                        if candidate_values[1] == "Write In":
                            office_entry[4].append(request.form.get('writein_name'))
                        else:
                            office_entry[4].append(None)
                        log_vote_event('log this final ' + str(office_entry))
                    elif form_name == 'VoteForMany':
                        selected_candidate_ids = request.form.getlist('candidates')
                        for candidate_id in selected_candidate_ids:
                            candidate_values = str(candidate_id).split('$')
                            office_entry[3].append([candidate_values[0], candidate_values[1]])
                            office_entry[4].append(candidate_values[1])
                        # Add the checked_options to the list of candidates voted for
                        # office_entry[3].extend(selected_candidate_ids)
                        break
            # Update the session with the modified office_dict
            # session['office_dict'] = office_dict
            log_vote_event('201 ' + group)
            next_office = get_next_office_for_group(session.get('office_dict'), group)
            log_vote_event('203 next_office ' + str(next_office))
            if next_office is None:
                if session['cnt'] + 1 < session['length']:
                    session['cnt'] += 1
                    log_vote_event('session cnt gggg' + str(session['cnt']))
                    log_vote_event ('session length gggg' + str(session['length']))
                    log_vote_event('grp_list gggg' + str(grp_list))
                    # session['group'] = grp_list.split('$')[session.get('cnt')]
                    log_vote_event('211 ' + str(session.get((grp_list))))
                    log_vote_event('Session grp_list: ' + str(session.get('grp_list', 'Not set')))
                    log_vote_event('Session cnt: ' + str(session.get('cnt', 'Not set')))
                    session['group'] = session['grp_list'].split('$')[session['cnt']]
                    log_vote_event('215 ' + str(session.get('group')))

                    next_office = get_next_office_for_group(session.get('office_dict'), session.get('group'))
                else:
                    log_vote_event('no more offices a')
                    vote_form = ReviewVotes()
                    return render_template('cast3.html', form=vote_form, group=session.get('group'),
                                           office_dict=session.get('office_dict'))
            log_vote_event('next_office ' + str(next_office))
            if next_office is not None:
                session['office'] = next_office[0]
                if next_office[2] == 1:  # vote for one
                    votes_form = VoteForOne()
                    grp = session.get('group', None)
                    candidate_choices = office_grp_query(grp, next_office[0])

                    print('candidate_choices ' + str(candidate_choices))
                    writein_candidate_id = has_writein_candidate(candidate_choices)
                    html_writein = 0
                    if writein_candidate_id is not None:
                        html_writein = writein_candidate_id
                        filtered_choices = remove_writein_candidate(candidate_choices, writein_candidate_id)
                        VoteForOne.candidate.choices = filtered_choices
                    else:
                        # html_writein = 0
                        VoteForOne.candidate.choices = candidate_choices

                    # session['office'] = next_office[0]
                    print('VoteForOne.candidate.choices ' + str(VoteForOne.candidate.choices))
                    return render_template('cast1.html', form=votes_form, office=next_office[0],
                                           candidates=VoteForOne.candidate.choices, grp=grp, html_writein=html_writein)

            if next_office is not None:
                if next_office[2] > 1:  # vote for one or more
                    votes_form = VoteForMany()
                    grp = session.get('group', None)
                    candidate_choices = office_grp_query(grp, next_office[0])
                    VoteForOne.candidate.choices = candidate_choices
                    return render_template('cast2.html', form=votes_form, office=next_office[0],
                                           candidates=candidate_choices, grp=grp, max_votes=next_office[2])
    vote_form = ReviewVotes()
    log_vote_event('no more offices b')
    return render_template('cast3.html', form=vote_form,
                           office_dict=session.get('office_dict'))
    # return 'no more offices'


def office_grp_query(grp, office):
    return_list = []
    candidates = db.session.query(Candidate, Classgrp, Office).select_from(Candidate).join(Classgrp).join(
        Office).filter(and_(Office.office_title == office, Classgrp.name == grp))
    for c in candidates:
        return_list.append(tuple((c.Candidate.id_candidate, c.Candidate.firstname + " " + c.Candidate.lastname)))
    return return_list


@vote.route('/edit_choice/<office_id>/<group>', methods=['POST', 'GET'])
def edit_choice(office_id, group):
    log_vote_event("edit_choice office " + office_id)
    log_vote_event("edit_choice group " + group)
    log_vote_event('edit_choice Session grp_list: ' + str(session.get('grp_list', 'Not set')))
    office_dict = session.get('office_dict', {})

    if group in office_dict:
        for office in office_dict[group]:
            if office[1] == int(office_id):
                log_vote_event('office edit_choice' + str(office))
                office[3] = []  # Clear the list of candidates voted for
                office[4] = []  # Clear the list of candidate names voted for
                log_vote_event('office edit_choice' + str(office))
                break

    # Update the session with the modified office_dict
    session['office_dict'] = office_dict
    session['review'] = True
    # Redirect to the cast route with the current group and token
    update_session_cnt_for_group(group)
    token = session.get('token_list_record', {}).get('token', '')
    return redirect(url_for('vote.cast', grp_list=group, token=token))

def find_group_position(grp_list, group_name):
    groups = grp_list.split('$')
    try:
        position = groups.index(group_name)
        return position
    except ValueError:
        return -1  # Group not found


def update_session_cnt_for_group(group_name):
    grp_list = session.get('grp_list', '')
    position = find_group_position(grp_list, group_name)
    if position != -1:
        session['cnt'] = position
        session['group'] = group_name
        log_vote_event(session['cnt'])
    else:
        log_vote_event(f"Group {group_name} not found in grp_list")


@vote.route('/post_ballot', methods=['POST'])
def post_ballot():
    if request.method == 'POST':
        office_dict = session.get('office_dict', {})
        token = session.get('token_list_record', {}).get('token', '')
        # Process the submitted ballot data
        # (Add your logic here to handle the ballot submission)
        for group in office_dict:
            for office in office_dict[group]:
                for item in office[3]:
                    if item[0] != 99:
                        new_vote = Votes(id_candidate=item[0], votes_token=token, votes_writein_name=office[4][0])
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
                log_vote_event("log the token does not exist")
                return "Error: Token record does not exist", 400
        except SQLAlchemyError as e:
            db.session.rollback()
            log_vote_event(f"Database error: {e}")

        # Clear the session data related to the ballot
        session.clear()
        home = current_app.config['HOME']
        return render_template('thank_you.html', home=home)


@vote.route('/vote_results', methods=['GET'])
def vote_results():

    if not date_after():
        flash('get results after voting end time ONLY ',
              category='danger')
        return redirect(url_for('mains.homepage'))
    
    form = VoteResults()
    form.choices_classgrp.choices = Classgrp.classgrp_query()
    summary_results = get_summary_results()
    candidates = [create_candidate_dataclass(item) for item in summary_results]
    mark_winner(candidates)

    # Set the candidates in the singleton
    candidate_singleton = CandidateDataClassSingleton()
    candidate_singleton.set_candidates(candidates)




    return render_template('vote_results.html',  form=form)


def create_candidate_dataclass(record):
    return CandidateDataClass(
        id_candidate=record[5],
        firstname=record[3],
        lastname=record[4],
        classgrp_name=record[0],
        office_title=record[1],
        vote_for=record[2],
        nbr_of_votes=record[6],
        winner=False  # Default value, can be updated later
    )

def mark_winner(candidates: list[CandidateDataClass]) -> list[CandidateDataClass]:
    # Group candidates by classgrp and office
    grouped_candidates = defaultdict(list)
    for candidate in candidates:
        key = (candidate.classgrp_name, candidate.office_title)
        grouped_candidates[key].append(candidate)

    # Find the winner(s) for each group
    for (classgrp, office), candidates in grouped_candidates.items():
        if candidates:
            if candidates[0].vote_for == 1:
                max_votes = max(candidates, key=lambda c: c.nbr_of_votes).nbr_of_votes
                for candidate in candidates:
                    if candidate.nbr_of_votes == max_votes:
                        candidate.winner_x = True
            else:
                # Sort candidates by number of votes in descending order
                candidates.sort(key=lambda c: c.nbr_of_votes, reverse=True)
                # Mark the top candidates as winners

                for i in range(min(candidates[0].vote_for, len(candidates))):
                    candidates[i].winner_x = True


    return candidates

def get_summary_results():
    results = db.session.query(
        Classgrp.name.label('group_name'),  # record[0]
        Office.office_title.label('office_title'),  # record[1]
        Office.office_vote_for.label('vote_for'),  # record[2]
        Candidate.firstname.label('candidate_firstname'),  # record[3]
        Candidate.lastname.label('candidate_lastname'),  # record[4]
        Candidate.id_candidate.label('candidate_id'),  # record[5]
        func.count(Votes.id_candidate).label('vote_total')  #
    ).join(Candidate, Votes.id_candidate == Candidate.id_candidate)\
     .join(Office, Candidate.id_office == Office.id_office)\
     .join(Classgrp, Candidate.id_classgrp == Classgrp.id_classgrp)\
     .group_by(Classgrp.name, Office.office_title, Candidate.firstname, Candidate.lastname)\
     .order_by(Classgrp.sortkey, Office.sortkey, func.count(Votes.id_candidate).desc())\
     .all()

    return results


@vote.route('/vote_results/search', methods=['GET'])
def vote_results_search():
    group = request.args.get('choices_classgrp', type=str)

    # Get the candidates from the singleton
    candidate_singleton = CandidateDataClassSingleton()
    candidates = candidate_singleton.get_candidates()

    results = filter_candidates_by_classgrp(candidates, group)

    return render_template('vote_classgrp_results.html', results=results)

def filter_candidates_by_classgrp(candidates: list[CandidateDataClass], classgrp_name: str) -> list[CandidateDataClass]:
    return [candidate for candidate in candidates if candidate.classgrp_name == classgrp_name]

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


def date_after():
    date = Dates.query.first()
    # Convert the epoch time to a datetime object
    start_date_time = datetime.fromtimestamp(date.start_date_time)
    end_date_time = datetime.fromtimestamp(date.end_date_time)

    # Get the current date time
    current_date_time = datetime.now()

    # Check if current date time is between start date time and end date time
    if current_date_time > end_date_time:
        return True
    else:
        return False


def get_next_office_for_group(office_dict, group_name):
    """
    Get the next office for a specific group or return None if there are no more offices.

    :param office_dict: A dictionary containing groups and their associated offices.
    :param group_name: The specific group for which the next office is to be retrieved.
    :return: The next office for the group or None.
    """
    # Check if the group exists in the office_dict
    log_vote_event('group_name gnofg' + group_name)
    log_vote_event('office_dict gnofg' + str(office_dict))
    if group_name not in office_dict:
        return None

    # Iterate through the offices for the specified group
    for office in office_dict[group_name]:
        # Check if the list of candidates voted for is empty (office[3])
        if not office[3]:  # If empty, this is the next office to vote for
            return office
    # If all offices have been voted for, return None
    return None


def are_all_classgrps_valid(grp_list):
    # Retrieve the list of valid classgrp names from the database
    valid_classgrps = [classgrp.name for classgrp in Classgrp.query.all()]

    # Split the grp_list into individual group names
    groups = grp_list.split('$')

    # Check if each group name in grp_list is in the list of valid classgrp names
    for group in groups:
        if group not in valid_classgrps:
            return False

    return True

def has_writein_candidate(candidate_choices):
    for candidate in candidate_choices:
        print('candidate[1] ' + candidate[1])
        if 'writein' in candidate[1].lower():
            print(" is true")
            return candidate[0]
    return None
def remove_writein_candidate(candidate_choices, writein_candidate_id):
    print('writein_candidate_id ' + str(writein_candidate_id))
    return [candidate for candidate in candidate_choices if candidate[0] != writein_candidate_id]



