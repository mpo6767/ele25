from flask import (render_template, url_for, flash,
                   redirect, request, Blueprint)
from election1.ballot.form import (CandidateForm, OfficeForm,
                                   ClassgrpForm, Candidate_reportForm, DatesForm)
from election1.models import Classgrp, Office, Candidate, Dates
from election1.extensions import db
from sqlalchemy.exc import SQLAlchemyError
import logging
from flask_login import current_user
from datetime import datetime

ballot = Blueprint('ballot', __name__)
logger = logging.getLogger(__name__)


def classgrp_query():
    return_list = []
    classgrp_data = db.session.query(Classgrp).order_by(Classgrp.sortkey)
    for c in classgrp_data:
        return_list.append(tuple((c.id_classgrp, c.name)))
    return return_list


@ballot.route('/office', methods=['POST', 'GET'])
def office():
    if check_dates() is False:
        flash('Please set the Election Dates before adding an office', category='danger')
        return redirect(url_for('mains.homepage'))
    if after_start_date():
        flash('You cannot add, delete or edit an office after the voting start time or Election Dates are '
              'empty', category='danger')
        return redirect(url_for('mains.homepage'))
    office_form = OfficeForm()
    if office_form.validate_on_submit():
        office_title = request.form['office_title']
        sortkey = request.form['sortkey']
        office_vote_for = request.form['office_vote_for']
        new_office = Office(office_title=office_title, sortkey=sortkey, office_vote_for=office_vote_for)

        try:
            db.session.add(new_office)
            db.session.commit()
            logger.info(
                'user ' + str(current_user.user_so_name) + ' has created the office titled ' + office_title)
            office_form.office_title.data = ''
            office_form.sortkey.data = None
            offices = Office.query.order_by(Office.sortkey)
            return render_template('office.html', form=office_form, offices=offices)
        except Exception as e:
            db.session.rollback()
            logger.info('There is an error ' + str(e) + ' while creating the office titled ' + office_title)
            flash('There was a problem inserting record ' + str(e), category='danger')
            office_form.office_title.data = ''
            office_form.sortkey.data = None
            offices = Office.query.order_by(Office.sortkey)
            return render_template('office.html', form=office_form, offices=offices)
    else:
        for err_msg in office_form.errors.values():
            flash(f'there is an error creating office: {err_msg}', category='danger')
            offices = Office.query.order_by(Office.sortkey)
            return render_template('office.html', form=office_form, offices=offices)

    office_form.office_title.data = ''
    office_form.sortkey.data = None
    # office_form.office_vote_for = 1
    offices = Office.query.order_by(Office.sortkey)
    return render_template('office.html', form=office_form, offices=offices)


@ballot.route('/deleteoffice/<int:xid>', methods=['POST', 'GET'])
def deleteoffice(xid):
    if check_dates() is False:
        flash('Please set the Election Dates before deleting an office', category='danger')
        return redirect(url_for('mains.homepage'))
    if after_start_date():
        flash('You cannot delete an office after the voting start time or Election Dates are empty ', category='danger')
        return redirect(url_for('mains.homepage'))
    office_to_delete = Office.query.get(xid)
    form = CandidateForm()
    if request.method == 'POST':

        try:
            db.session.delete(office_to_delete)
            db.session.commit()
            logger.info(
                'user ' + str(
                    current_user.user_so_name) + ' has deleted the office titled ' + office_to_delete.office_title)
            flash('successfully deleted record', category='success')
            return redirect('/office')
        except SQLAlchemyError as e:
            db.session.rollback()
            flash('There was a problem deleting record' + str(e))
            return redirect('/office')
    else:

        candidates = db.session.query(Candidate, Classgrp, Office).select_from(Candidate).join(Classgrp).join(
            Office).order_by(Classgrp.sortkey, Office.sortkey).where(Candidate.id_office == xid)
        return render_template('office_candidate_delete.html', form=form, candidates=candidates,
                               office_to_delete=office_to_delete)


@ballot.route('/updateoffice/<int:xid>', methods=['GET', 'POST'])
def updateoffice(xid):
    if check_dates() is False:
        flash('Please set the Election Dates before updating an office', category='danger')
        return redirect(url_for('mains.homepage'))
    if after_start_date():
        flash('You cannot edit an office after the voting start time or Election Dates are empty ', category='danger')
        return redirect(url_for('mains.homepage'))
    office_form = OfficeForm()
    office_to_update = Office.query.get_or_404(xid)
    print(office_to_update.office_title)
    if request.method == "POST":
        office_to_update.office_title = request.form['office_title']
        office_to_update.sortkey = request.form['sortkey']
        try:
            db.session.commit()
            logger.info(
                'user ' + str(
                    current_user.user_so_name) + ' has edited the office titled ' + office_to_update.office_title)
            flash('successfully updates record', category='success')
            office_form.office_title.data = ''
            office_form.sortkey.data = ''
            offices = Office.query.order_by(Office.sortkey)
            return render_template('office.html', form=office_form, offices=offices)
        except SQLAlchemyError as e:
            db.session.rollback()
            flash('There was a problem updating record record' + str(e), category='danger')
            office_form.office_title.data = ''
            office_form.sortkey.data = ''
            offices = Office.query.order_by(Office.sortkey)
            return render_template('office.html', form=office_form, offices=offices)
    else:
        return render_template('update_office.html', form=office_form,
                               office_to_update=office_to_update)


@ballot.route('/classgrp', methods=['POST', 'GET'])
def classgrp():
    if check_dates() is False:
        flash('Please set the Election Dates before adding a class or group', category='danger')
        return redirect(url_for('mains.homepage'))
    if after_start_date():
        flash('You cannot add or delete a class or a group after the voting start time or Election Dates are empty ',
              category='danger')
        return redirect(url_for('mains.homepage'))
    classgrp_form = ClassgrpForm()
    if classgrp_form.validate_on_submit():
        classgrp_name = request.form['name']
        sortkey = request.form['sortkey']
        new_classgrp = Classgrp(name=classgrp_name, sortkey=sortkey)
        db.session.add(new_classgrp)
        db.session.commit()
        flash('successfully added record', category='success')
    else:
        for err_msg in classgrp_form.errors.values():
            flash(f'there is an error creating a class or group: {err_msg}', category='danger')
            classgrps = Classgrp.query.order_by(Classgrp.sortkey)
            return render_template('classgrp.html', form=classgrp_form, classgrps=classgrps)

    classgrp_form.name.data = ''
    classgrp_form.sortkey.data = None
    classgrps = Classgrp.query.order_by(Classgrp.sortkey)

    return render_template('classgrp.html', form=classgrp_form, classgrps=classgrps)


@ballot.route('/deleteclass/<int:xid>')
def deleteclass(xid):
    if check_dates() is False:
        flash('Please set the Election Dates before deleting a class or group', category='danger')
        return redirect(url_for('mains.homepage'))
    if after_start_date():
        flash('You cannot delete an class or group after the voting start time or Election Dates are empty ',
              category='danger')
        return redirect(url_for('mains.homepage'))

    classgrp_to_delete = Classgrp.query.get_or_404(xid)

    try:
        db.session.delete(classgrp_to_delete)
        db.session.commit()
        # flash('successfully deleted record',category='success')
        return redirect('/classgrp')
    except SQLAlchemyError as e:
        db.session.rollback()
        flash('There was a problem deleting record' + str(e), category='danger')
        return redirect('/classgrp')


@ballot.route('/updateclass/<int:xid>', methods=['GET', 'POST'])
def updateclass(xid):
    if check_dates() is False:  # Check if the dates are set
        flash('Please set the Election Dates before updating a class or group', category='danger')
        return redirect(url_for('mains.homepage'))
    if after_start_date():
        flash('You cannot edit a class or group after the voting start time or Election Dates are empty ',
              category='danger')
        return redirect(url_for('mains.homepage'))
    classgrp_form = ClassgrpForm()
    classgrp_to_update = Classgrp.query.get_or_404(xid)
    print(classgrp_to_update.name)
    if request.method == "POST":
        classgrp_to_update.name = request.form['name']
        classgrp_to_update.sortkey = request.form['sortkey']
        try:
            db.session.commit()
            flash('successfully updates record', category='success')
            classgrp_form.name.data = ''
            classgrp_form.sortkey.data = ''
            classgrps = Classgrp.query.order_by(Classgrp.sortkey)
            return render_template('classgrp.html', form=classgrp_form, classgrps=classgrps)
        except SQLAlchemyError as e:
            db.session.rollback()
            flash('There was a problem updating record record ' + str(e), category='danger')
            classgrp_form.name.data = ''
            classgrp_form.sortkey.data = ''
            classgrps = Classgrp.query.order_by(Classgrp.sortkey)
            return render_template('classgrp.html', form=classgrp_form, classgrps=classgrps)
    else:
        return render_template('update_classgrp.html', form=classgrp_form,
                               classgrp_to_update=classgrp_to_update)


@ballot.route("/candidate_report", methods=['GET', 'POST'])
def candidate_report():
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


@ballot.route('/candidate', methods=['GET', 'POST'])
def candidate():
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
        return render_template('candidate.html', form=form)


@ballot.route('/candidate/search')
def candidate_search():
    group = request.args.get('choices_classgrp', type=int)
    candidates = db.session.query(Candidate, Classgrp, Office).select_from(Candidate).join(Classgrp).join(
        Office).order_by(Classgrp.sortkey, Office.sortkey).where(Classgrp.id_classgrp == group)
    return render_template('candidate_search_results.html',  candidates=candidates)


@ballot.route('/deletecandidate/<int:xid>')
def deletecandidate(xid):
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


@ballot.route('/dates', methods=['GET', 'POST'])
def dates():
    form = DatesForm()
    if request.method == 'POST':
        if form.validate_on_submit():

            datetime_str = request.form.get('start_date_time').replace("T", " ")
            datetime_etr = request.form.get('end_date_time').replace("T", " ")

            datetime_object_start = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M')
            datetime_object_end = datetime.strptime(datetime_etr, '%Y-%m-%d %H:%M')

            epoch_start_time = int(datetime_object_start.timestamp())
            epoch_end_time = int(datetime_object_end.timestamp())

            new_dates = Dates(start_date_time=epoch_start_time, end_date_time=epoch_end_time)
            db.session.add(new_dates)
            db.session.commit()

            # # Log the start and end dates
            # logger.info(f'user ' + str(current_user.user_so_name) + " has added the following dates:"
            #             "Start date: {datetime_object_start}, End date: {datetime_object_end}")

            # Log the start and end dates
            logger.info('user ' + str(current_user.user_so_name) + " has added the following dates:")

            logger.info(f'Start date: {datetime_object_start}, End date: {datetime_object_end}')

            return redirect(url_for('mains.homepage'))

    edate_dict = {}
    edates = Dates.query.all()
    if edates is not None:
        for edate in edates:
            new_edate_dict = {
                "id": edate.iddates,
                "start": datetime.fromtimestamp(edate.start_date_time),
                "end": datetime.fromtimestamp(edate.end_date_time)
            }
            edate_dict.update(new_edate_dict)

    return render_template('dates.html', form=form, edate_dict=edate_dict)


@ballot.route('/deletedates/')
def deletedates():
    # Get the first set of datee in the table because we are only storing one set of dates
    date_to_delete = Dates.query.first()
    start_date: datetime = datetime.fromtimestamp(date_to_delete.start_date_time)
    logger.info(
        'user {0} has deleted the date with start date of {1}'.format(str(current_user.user_so_name), str(start_date)))
    try:
        db.session.delete(date_to_delete)
        db.session.commit()
        flash('successfully deleted record')
        return redirect('/dates')
    except SQLAlchemyError as e:
        db.session.rollback()
        flash('There was a problem deleting record ' + str(e))
        return redirect('/dates')


def after_start_date():
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
    date = Dates.query.first()
    if date is None:
        return False
    else:
        return True
