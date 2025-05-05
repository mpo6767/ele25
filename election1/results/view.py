from datetime import datetime
from flask import Blueprint, request, render_template
from election1.models import Classgrp, Office, Candidate, Tokenlist, Votes, Dates
from election1.vote.form import  VoteResults
from election1.dclasses import CandidateDataClass
from collections import defaultdict

results = Blueprint('results', __name__)

class CandidateDataClassSingleton:
    _instance = None
    _candidates = []

    # def __new__(cls):
    #     if cls._instance is None:
    #         cls._instance = super(CandidateDataClassSingleton, cls).__new__(cls)
    #     return cls._instance

    def __new__(cls):
        if cls._instance is None:
            cls._instance = object.__new__(cls)  # Use `object.__new__` to avoid recursion
        return cls._instance

    def set_candidates(self, candidates: list[CandidateDataClass]):
        self._candidates = candidates
        print('CandidateDataClassSingleton set_candidates')

    def get_candidates(self) -> list[CandidateDataClass]:
        print('CandidateDataClassSingleton get_candidates')
        return self._candidates


@results.route('/vote_results', methods=['GET'])
def vote_results():

    # if not date_after():
    #     flash('get results after voting end time ONLY ',
    #           category='danger')
    #     return redirect(url_for('mains.homepage'))

    form = VoteResults()
    form.choices_classgrp.choices = Classgrp.classgrp_query()
    print('form.choices_classgrp.choices ' + str(form.choices_classgrp.choices))
    summary_results = Candidate.get_summary_results()
    print('summary_results ' + str(summary_results))

    candidates = [create_candidate_dataclass(item) for item in summary_results]
    print('candidates ' + str(candidates))
    mark_winner(candidates)

    # Set the candidates in the singleton
    candidate_singleton = CandidateDataClassSingleton()
    candidate_singleton.set_candidates(candidates)




    return render_template('vote_results.html',  form=form)


def create_candidate_dataclass(record):
    print('create_candidate_dataclass record ' + str(record))
    print('IN CCD')
    return CandidateDataClass(
        id_candidate=record[5],
        firstname=record[3],
        lastname=record[4],
        classgrp_name=record[0],
        office_title=record[1],
        vote_for=record[2],

        nbr_of_votes=record[6],
        write_in_allowed=False,
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
                        candidate.winner = True
            else:
                # Sort candidates by number of votes in descending order
                candidates.sort(key=lambda c: c.nbr_of_votes, reverse=True)
                # Mark the top candidates as winners

                for i in range(min(candidates[0].vote_for, len(candidates))):
                    candidates[i].winner = True


    return candidates

# def get_summary_results():
#     results = db.session.query(
#         Classgrp.name.label('group_name'),  # record[0]
#         Office.office_title.label('office_title'),  # record[1]
#         Office.office_vote_for.label('vote_for'),  # record[2]
#         Candidate.firstname.label('candidate_firstname'),  # record[3]
#         Candidate.lastname.label('candidate_lastname'),  # record[4]
#         Candidate.id_candidate.label('candidate_id'),  # record[5]
#         func.count(Votes.id_candidate).label('vote_total')  #
#     ).join(Candidate, Votes.id_candidate == Candidate.id_candidate)\
#      .join(Office, Candidate.id_office == Office.id_office)\
#      .join(Classgrp, Candidate.id_classgrp == Classgrp.id_classgrp)\
#      .group_by(Classgrp.name, Office.office_title, Candidate.firstname, Candidate.lastname)\
#      .order_by(Classgrp.sortkey, Office.sortkey, func.count(Votes.id_candidate).desc())\
#      .all()
#
#     return results


@results.route('/vote_results/search', methods=['GET'])
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

