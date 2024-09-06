from datetime import datetime
from flask import render_template, url_for, flash, redirect, request, Blueprint
from election1.candidate.form import CandidateForm, Candidate_reportForm, classgrp_query
from election1.office.view import office_query
from election1.models import Classgrp, Office, Candidate
from election1.extensions import db
from sqlalchemy.exc import SQLAlchemyError
from election1.utils import is_user_authenticated
import logging

candidate = Blueprint('candidate', __name__)
logger = logging.getLogger(__name__)


def classgrp_query():
    return_list = []
    classgrp_data = db.session.query(Classgrp).order_by(Classgrp.sortkey)
    for c in classgrp_data:
        return_list.append(tuple((c.id_classgrp, c.name)))
    return return_list


@candidate.route("/candidate_report", methods=['GET', 'POST'])
def candidate_report():

    if not is_user_authenticated():
        return redirect(url_for('admins.login'))

    form = Candidate_reportForm()
    list_of_offices = db.session.query(Office).all()
    if request.method == 'POST':
        choices_classgrp = request.form['choices_classgrp']
        choices_office = request.form['choices_office']

        # the first if determines if the choice_office is an int 0
        # I built the candidate_report.html to add a choice of 'All Offices' which is not in the DB
        # I pass list_of_offices to the html and build the select offices manually fo this html
        if int(choices_office) == 0:
            candidates = db.session.query(Candidate, Classgrp, Office).select_from(Candidate).join(Classgrp).join(
                Office).filter(Classgrp.id_classgrp == choices_classgrp)
            return render_template("candidate_report.html",
                                   form=form, candidates=candidates, list_of_offices=list_of_offices)
        else:
            candidates = db.session.query(Candidate, Classgrp, Office).select_from(Candidate).join(Classgrp).join(
                Office).filter(Classgrp.id_classgrp == choices_classgrp, Office.id_office == choices_office)
            return render_template("candidate_report.html",
                                   form=form, candidates=candidates, list_of_offices=list_of_offices)

    else:
        form.choices_classgrp.choices = classgrp_query()
        return render_template("candidate_report.html", form=form, list_of_offices=list_of_offices)


@candidate.route('/candidate', methods=['GET', 'POST'])
def candidate_view():

    if not is_user_authenticated():
        return redirect(url_for('admins.login'))

    if check_dates() is False:
        flash('Please set the Election Dates before adding a candidate', category='danger')
        return redirect(url_for('mains.homepage'))

    if after_start_date():
        flash('You cannot add or delete a candidate after the voting start time or Election Dates are empty ',
              category='danger')
        return redirect(url_for('mains.homepage'))

    form = CandidateForm()
    if request.method == 'POST':
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        choices_classgrp = request.form['choices_classgrp']
        choices_office = request.form['choices_office']

        # Check if a valid option is selected
        if choices_classgrp == "Please select":
            flash('Please select a valid option for class', category='danger')
            form.choices_classgrp.choices = classgrp_query()
            form.choices_office.choices = office_query()
            return render_template('candidate.html', form=form)

        if choices_office == "Please select":
            flash('Please select a valid option for office', category='danger')
            form.choices_office.choices = office_query()
            form.choices_classgrp.choices = classgrp_query()
            return render_template('candidate.html', form=form)

        new_candidate = Candidate(firstname=firstname,
                                  lastname=lastname,
                                  id_classgrp=choices_classgrp,
                                  id_office=choices_office)

        try:
            db.session.add(new_candidate)
            db.session.commit()
            return redirect(url_for('ballot.candidate'))
        except SQLAlchemyError as e:
            db.session.rollback()
            flash('problem adding candidate ' + str(e), category='danger')
            return redirect('/candidate')
    else:
        form.choices_classgrp.choices = classgrp_query()
        form.choices_office.choices = office_query()
        return render_template('candidate.html', form=form)


@candidate.route('/candidate/search')
def candidate_search():
    group = request.args.get('choices_classgrp', type=int)
    candidates = db.session.query(Candidate, Classgrp, Office).select_from(Candidate).join(Classgrp).join(
        Office).order_by(Classgrp.sortkey, Office.sortkey).where(Classgrp.id_classgrp == group)
    return render_template('candidate_search_results.html',  candidates=candidates)


@candidate.route('/deletecandidate/<int:xid>')
def deletecandidate(xid):

    if not is_user_authenticated():
        return redirect(url_for('admins.login'))

    candidate_to_delete = Candidate.query.get_or_404(xid)

    try:
        db.session.delete(candidate_to_delete)
        db.session.commit()
        flash('successfully deleted record')
        return redirect('/candidate')
    except SQLAlchemyError as e:
        db.session.rollback()
        flash('There was a problem deleting record ' + str(e))
        return redirect('/candidate')


def after_start_date():
    from election1.models import Dates  # Local import to avoid circular import
    date = Dates.query.first()
    start_date_time = datetime.fromtimestamp(date.start_date_time)

    # Get the current date time
    current_date_time = datetime.now()

    # Check if current date time is less than start date time
    if current_date_time > start_date_time:
        return True
    else:
        return False


def check_dates():
    from election1.models import Dates  # Local import to avoid circular import
    date = Dates.query.first()
    if date is None:
        return False
    else:
        return True
