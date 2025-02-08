from flask import (render_template, url_for, flash,
                   redirect, request, Blueprint, current_app)
from election1.dates.form import ( DatesForm)
from election1.models import  Dates
from election1.extensions import db
from sqlalchemy.exc import SQLAlchemyError
import logging
from flask_login import current_user
from datetime import datetime

from election1.utils import is_user_authenticated, session_check

dates = Blueprint('dates', __name__)
logger = logging.getLogger(__name__)

@dates.before_request
def check_session_timeout():
    if not session_check():
        home = current_app.config['HOME']
        error = 'idle timeout '
        return render_template('session_timeout.html', error=error, home=home)

@dates.route('/dates', methods=['GET', 'POST'])
def dates_view():

    if not is_user_authenticated():
        return redirect(url_for('admins.login'))

    logger.info('user ' + str(current_user.user_so_name) + " has entered dates page")

    form = DatesForm()

    if request.method == 'POST':
        if form.validate_on_submit():
            print("form validated")

            datetime_str = request.form.get('start_date_time').replace("T", " ")
            datetime_etr = request.form.get('end_date_time').replace("T", " ")

            datetime_object_start = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M')
            datetime_object_end = datetime.strptime(datetime_etr, '%Y-%m-%d %H:%M')

            epoch_start_time = int(datetime_object_start.timestamp())
            epoch_end_time = int(datetime_object_end.timestamp())

            new_dates = Dates(start_date_time=epoch_start_time, end_date_time=epoch_end_time)
            db.session.add(new_dates)
            db.session.commit()

            logger.info('user ' + str(current_user.user_so_name) + " has added the following dates:")
            logger.info(f'Start date: {datetime_object_start}, End date: {datetime_object_end}')

            return redirect(url_for('mains.homepage'))
        else:
            print("form did not validate")
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f"Error in {getattr(form, field).label.text}: {error}", 'danger')

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


@dates.route('/deletedates/')
def deletedates():

    if not is_user_authenticated():
        return redirect(url_for('admins.login'))

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


