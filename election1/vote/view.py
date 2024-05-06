from flask import Blueprint, request, redirect, flash, render_template, url_for
from election1.vote.form import VotesForm
from election1.models import Classgrp, Office, Candidate, Tokenlist, Votes
from election1.extensions import db

vote = Blueprint('vote', __name__)


def office_grp_query(grp, office):
    return_list = []
    candidates = db.session.query(Candidate, Classgrp, Office).select_from(Candidate).join(Classgrp).join(
        Office).where( Office.office_title == office and Classgrp == grp )
    for c in candidates:
        return_list.append(tuple((c.Candidate.id_candidate, c.Candidate.firstname + " " + c.Candidate.lastname)))
    return return_list


@vote.route('/cast/<grp>/<token>', methods=['POST', 'GET'])
def cast(grp, token):
    print(grp + token)
    votes_form = VotesForm()
    hold_token = token
    hold_grp = grp

    if hold_grp == "Freshman":
        grp_key = 1
    elif hold_grp == "Sophomore":
        grp_key = 2
    elif hold_grp == "Junior":
        grp_key = 3
    elif hold_grp == "Senior":
        grp_key = 4
    else:
        print("bad group")
    # result = db.session.query(Tokenlist).filter(Tokenlist.vote_submitted_date_time == 'abc')
    # result = db.session.query(Tokenlist).filter(Tokenlist.token == '55b03a72c80b4a5ac26a6e5c584a774141eb414e20abe450e5a171890e6cad202b48e7f9a5e45efca6d3a4808cf23a959e33b3cdf8fc2d61')
    # if result:
    # print(Tokenlist.query.filter_by(token=token, vote_submitted_date_time='').count())
    if request.method == 'GET':
        token_list = db.session.query(Tokenlist).filter_by(token=token).first
        # if Tokenlist.query.filter_by(token=token).count() == 1:
        if token_list:
            if Tokenlist.query.filter_by(token=token, vote_submitted_date_time='').count() == 1:
                print('you can vote')
            else:
                print('you already voted')
        else:
            print('you have a bad token')
    else:
        print(request.method)
        # request.method == 'POST ':
        print('count the vote')
        votesForm = VotesForm()
        president = request.form['p_candidate']
        print(president)
        vpresident = request.form['vp_candidate']
        print(vpresident)
        secretary = request.form['s_candidate']
        print(secretary)
        treasurer = request.form['t_candidate']
        print(treasurer)
        try:
            if president != "99":
                president_vote = Votes(votes_token=hold_token, id_canndidate=int(president))
                db.session.add(president_vote)
            if vpresident != "99":
                vpresident_vote = Votes(votes_token=hold_token, id_canndidate=int(vpresident))
                db.session.add(vpresident_vote)
            if secretary != "99":
                secretary_vote = Votes(votes_token=hold_token, id_canndidate=int(secretary))
                db.session.add(secretary_vote)
            if treasurer != "99":
                treasurer_vote = Votes(votes_token=hold_token, id_canndidate=int(treasurer))
                db.session.add(treasurer_vote)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print("we have an exception " + e)
            return render_template('homepage.html')


    votes_form = VotesForm()
    votes_form.p_candidate.choices = office_grp_query(grp, 'President')
    votes_form.vp_candidate.choices = office_grp_query(grp, 'Vice President')
    votes_form.s_candidate.choices = office_grp_query(grp, 'Secretary')
    votes_form.t_candidate.choices = office_grp_query(grp, 'Treasurer')

    return render_template('cast.html', form=votes_form)
