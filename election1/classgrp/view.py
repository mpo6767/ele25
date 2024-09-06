from flask import (render_template, url_for, flash,
                   redirect, request, Blueprint)

from election1.classgrp.form import ClassgrpForm
# from election1.ballot.form import (CandidateForm, OfficeForm,
#                                    ClassgrpForm, Candidate_reportForm, DatesForm, classgrp_query)
from election1.models import Classgrp
from election1.extensions import db
from sqlalchemy.exc import SQLAlchemyError
import logging
from flask_login import current_user
from datetime import datetime

classgrp = Blueprint('classgrp', __name__)
logger = logging.getLogger(__name__)


def classgrp_query():
    return_list = []
    classgrp_data = db.session.query(Classgrp).order_by(Classgrp.sortkey)
    for c in classgrp_data:
        return_list.append(tuple((c.id_classgrp, c.name)))
    return return_list


def is_user_authenticated():
    return current_user.is_authenticated


@classgrp.route('/classgrp', methods=['POST', 'GET'])
def classgrp_view():

    if not is_user_authenticated():
        return redirect(url_for('admins.login'))

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


@classgrp.route('/deleteclass/<int:xid>')
def deleteclass(xid):

    if not is_user_authenticated():
        return redirect(url_for('admins.login'))

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


@classgrp.route('/updateclass/<int:xid>', methods=['GET', 'POST'])
def updateclass(xid):

    if not is_user_authenticated():
        return redirect(url_for('admins.login'))

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
