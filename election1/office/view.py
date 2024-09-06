from flask import (render_template, url_for, flash,
                   redirect, request, Blueprint)
from election1.office.form import (OfficeForm)

from election1.models import Classgrp, Office, Candidate
from election1.extensions import db
from sqlalchemy.exc import SQLAlchemyError
import logging
from flask_login import current_user
from datetime import datetime

from election1.utils import is_user_authenticated

office = Blueprint('office', __name__)
logger = logging.getLogger(__name__)

def office_query():
    return_list = []
    office_data = db.session.query(Office).order_by(Office.sortkey)
    for o in office_data:
        return_list.append(tuple((o.id_office, o.office_title)))
    return return_list



@office.route('/office', methods=['POST', 'GET'])
def office_view():

    if not is_user_authenticated():
        return redirect(url_for('admins.login'))

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


@office.route('/deleteoffice/<int:xid>', methods=['POST', 'GET'])
def deleteoffice(xid):

    if not is_user_authenticated():
        return redirect(url_for('admins.login'))

    if check_dates() is False:
        flash('Please set the Election Dates before deleting an office', category='danger')
        return redirect(url_for('mains.homepage'))

    if after_start_date():
        flash('You cannot delete an office after the voting start time or Election Dates are empty ', category='danger')
        return redirect(url_for('mains.homepage'))

    office_to_delete = Office.query.get(xid)
    form = OfficeForm()

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


@office.route('/updateoffice/<int:xid>', methods=['GET', 'POST'])
def updateoffice(xid):

    if not is_user_authenticated():
        return redirect(url_for('admins.login'))

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
        office_to_update.office_vote_for = request.form['office_vote_for']
        try:
            db.session.commit()
            logger.info(
                'user ' + str(
                    current_user.user_so_name) + ' has edited the office titled ' + office_to_update.office_title)
            flash('successfully updates record', category='success')
            # office_form.office_title.data = ''
            # office_form.sortkey.data = 0
            # office_form.office_vote_for.data = 1
            offices = Office.query.order_by(Office.sortkey)
            return redirect('/office')
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
