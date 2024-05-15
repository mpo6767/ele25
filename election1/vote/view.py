from pathlib import Path
from datetime import datetime
import xlsxwriter
from flask import Blueprint, request, render_template, redirect
from election1.extensions import db
from election1.models import Classgrp, Office, Candidate, Tokenlist, Votes
from election1.vote.form import VotesForm
from election1.utils import get_token
from sqlalchemy.exc import SQLAlchemyError


vote = Blueprint('vote', __name__)


def office_grp_query(grp, office):
    return_list = []
    candidates = db.session.query(Candidate, Classgrp, Office).select_from(Candidate).join(Classgrp).join(
        Office).where(Office.office_title == office and Classgrp == grp)
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
        token_list = Tokenlist.query.filter_by(token=token).first()
        if token_list:
            if Tokenlist.query.filter_by(token=token, vote_submitted_date_time=None).count() == 1:
                print('you can vote')
                token_list.vote_submitted_date_time=datetime.now()
            else:
                print('you already voted')
                return render_template('previous_vote.html')
        else:
            print('you have a bad token')
            return render_template('bad_token.html')
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
                print(hold_token + " " + president)
                president_vote = Votes(votes_token=hold_token, id_candidate=president)
                db.session.add(president_vote)
                print('president_vote')
            if vpresident != "99":
                vpresident_vote = Votes(votes_token=hold_token, id_candidate=int(vpresident))
                db.session.add(vpresident_vote)
                print('vpresident_vote')
            if secretary != "99":
                secretary_vote = Votes(votes_token=hold_token, id_candidate=int(secretary))
                db.session.add(secretary_vote)
                print('secretary_vote')
            if treasurer != "99":
                treasurer_vote = Votes(votes_token=hold_token, id_candidate=int(treasurer))
                db.session.add(treasurer_vote)
                print('treasurer_vote')
            token_list = Tokenlist.query.filter_by(token=token).first()
            token_list.vote_submitted_date_time = datetime.now()
            db.session.commit()

        except SQLAlchemyError as e:
            db.session.rollback()
            print("we have an exception " + e)
            return render_template('unexpected_error.html')


    votes_form = VotesForm()
    print("1")
    votes_form.p_candidate.choices = office_grp_query(grp, 'President')
    print("1")
    votes_form.vp_candidate.choices = office_grp_query(grp, 'Vice President')
    print("1")
    votes_form.s_candidate.choices = office_grp_query(grp, 'Secretary')
    print("1")
    votes_form.t_candidate.choices = office_grp_query(grp, 'Treasurer')
    print("1")

    print("fall through")

    return render_template('successful_vote.html')
    # return render_template('homepage.html')

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
            worksheet.write(row, col, 'http://127.0.0.1:5000/cast/Freshman/' + token)
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
