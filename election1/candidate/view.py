from flask import render_template, url_for, flash, redirect, request, Blueprint, current_app
from flask_login import current_user

from election1.candidate.form import CandidateForm, Candidate_reportForm,  WriteinCandidateForm
from election1.models import Classgrp, Office, Candidate, WriteinCandidate, Dates
from election1.extensions import db
from sqlalchemy.exc import SQLAlchemyError
from election1.utils import is_user_authenticated, session_check
import logging

candidate = Blueprint('candidate', __name__)
logger = logging.getLogger(__name__)

@candidate.before_request
def check_session_timeout():
    if not session_check():
        home = current_app.config['HOME']
        error = 'idle timeout '
        return render_template('session_timeout.html', error=error, home=home)


@candidate.route('/writein_candidate', methods=['GET', 'POST'])
def writein_candidate():
    logger.info('user ' + str(current_user.user_so_name) + " has entered write in candidate page")

    if not is_user_authenticated():
        return redirect(url_for('admins.login'))

    if Dates.check_dates() is False:
        flash('Please set the Election Dates before registering write in ', category='danger')
        return redirect(url_for('mains.homepage'))

    if Dates.after_start_date():
        flash('You cannot register a write in after the voting start time or Election Dates are empty ',
              category='danger')
        return redirect(url_for('mains.homepage'))

    form = WriteinCandidateForm()

    if request.method == 'POST':
        print('request.form *** ' )
        writein_candidate_name = request.form['writein_candidate_name']
        choices_classgrp = request.form['choices_classgrp']
        choices_office = request.form['choices_office']

        # Check if a valid option is selected
        if choices_classgrp == "Please select":
            flash('Please select a valid option for class', category='danger')
            form.choices_classgrp.choices = Classgrp.classgrp_query()
            form.choices_office.choices = Office.office_query()
            candidates = WriteinCandidate.get_writein_candidates_sorted()
            return render_template('writein_candidate.html', form=form , candidates=candidates)

        if choices_office == "Please select":
            flash('Please select a valid option for office', category='danger')
            form.choices_office.choices = Office.office_query()
            form.choices_classgrp.choices = Classgrp.classgrp_query()
            candidates = WriteinCandidate.get_writein_candidates_sorted()
            return render_template('writein_candidate.html', form=form, candidates=candidates)

        if WriteinCandidate.check_existing_writein_candidate(writein_candidate_name, choices_classgrp, choices_office) is True:
            flash('Write-in candidate already exists for this class and office', category='danger')
            return redirect(url_for('candidate.writein_candidate'))

        new_writein_candidate = WriteinCandidate(writein_candidate_name=writein_candidate_name,
                                                 id_classgrp=choices_classgrp,
                                                 id_office=choices_office)

        try:
            Candidate.check_and_insert_writein_candidate(choices_classgrp, choices_office)
            db.session.add(new_writein_candidate)

            db.session.commit()
            return redirect(url_for('candidate.writein_candidate'))
        except SQLAlchemyError as e:
            db.session.rollback()
            flash('problem adding write-in candidate registration' + str(e), category='danger')
            return redirect(url_for('candidate.writein_candidate'))

    form.choices_classgrp.choices = Classgrp.classgrp_query()
    form.choices_office.choices = Office.office_query()
    candidates = WriteinCandidate.get_writein_candidates_sorted()
    return render_template('writein_candidate.html', form=form, candidates=candidates)




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
        print('-- ' + choices_office)
        if int(choices_office) == 0:
            candidates = Candidate.get_candidates_for_all_offices_by_classgrp(choices_classgrp)
            return render_template("candidate_report.html",
                                   form=form, candidates=candidates, list_of_offices=list_of_offices)
        else:
            candidates = Candidate.get_candidates_for_specific_office_by_classgrp(choices_classgrp, choices_office)
            return render_template("candidate_report.html",
                                   form=form, candidates=candidates, list_of_offices=list_of_offices)

    else:
        form.choices_classgrp.choices = Classgrp.classgrp_query()
        return render_template("candidate_report.html", form=form, list_of_offices=list_of_offices)


@candidate.route('/candidate', methods=['GET', 'POST'])
def candidate_view():
    logger.info('user ' + str(current_user.user_so_name) + " has entered candidate page")

    if not is_user_authenticated():
        return redirect(url_for('admins.login'))

    if Dates.check_dates() is False:
        flash('Please set the Election Dates before adding a candidate', category='danger')
        return redirect(url_for('mains.homepage'))

    if Dates.after_start_date():
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
            form.choices_classgrp.choices = Classgrp.classgrp_query()
            form.choices_office.choices = Office.office_query()
            return render_template('candidate.html', form=form)

        if choices_office == "Please select":
            flash('Please select a valid option for office', category='danger')
            form.choices_office.choices = Office.office_query()
            form.choices_classgrp.choices = Classgrp.classgrp_query()
            return render_template('candidate.html', form=form)

        if Candidate.check_existing_candidate(firstname, lastname, choices_classgrp) is True:
            flash('Candidate already exists for this class', category='danger')
            return render_template('candidate.html', form=form)

        new_candidate = Candidate(firstname=firstname,
                                  lastname=lastname,
                                  id_classgrp=choices_classgrp,
                                  id_office=choices_office)

        try:
            db.session.add(new_candidate)
            db.session.commit()
            logger.info('user ' + str(current_user.user_so_name) + " has created " + firstname + ' ' + lastname)
            flash('successfully  adding candidate ', category='danger')
            return redirect(url_for('candidate.candidate_view'))
        except SQLAlchemyError as e:
            db.session.rollback()
            flash('problem adding candidate ' + str(e), category='danger')
            return redirect('/candidate')
    else:
        form.choices_classgrp.choices = Classgrp.classgrp_query()
        form.choices_office.choices = Office.office_query()
        return render_template('candidate.html', form=form)


@candidate.route('/candidate/search')
def candidate_search():
    group = request.args.get('choices_classgrp', type=int)
    candidates = Candidate.candidate_search(group)
    return render_template('candidate_search_results.html',  candidates=candidates)


@candidate.route('/deletecandidate/<int:xid>')
def deletecandidate(xid):

    if not is_user_authenticated():
        return redirect(url_for('admins.login'))

    candidate_to_delete = Candidate.query.get_or_404(xid)

    try:
        db.session.delete(candidate_to_delete)
        db.session.commit()
        flash('successfully deleted record', category='danger')
        logger.info('user ' + str(current_user.user_so_name) + " has deleted " + candidate_to_delete.firstname + ' ' + candidate_to_delete.lastname)
        return redirect('/candidate')
    except SQLAlchemyError as e:
        db.session.rollback()
        flash('There was a problem deleting record ' + str(e))
        return redirect('/candidate')


