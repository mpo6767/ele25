from flask import Blueprint, request, redirect, flash, render_template, url_for, current_app
from election1.admins.form import UserForm
from election1.extensions import db
from election1.models import User
from sqlalchemy.exc import IntegrityError
import logging
from werkzeug.security import generate_password_hash
from flask_login import current_user
from election1.utils import session_check

admins = Blueprint('admins', __name__)
logger = logging.getLogger(__name__)

@admins.before_request
def check_session_timeout():
    if not session_check():
        home = current_app.config['HOME']
        error = 'idle timeout '
        return render_template('session_timeout.html', error=error, home=home)


@admins.route('/user_admin', methods=['GET', 'POST'])
def user_admin():
    """
    Handle user administration, including adding new users and displaying existing users.
    """
    form = UserForm()
    if request.method == 'POST' and form.validate():
        user_firstname = request.form['user_firstname']
        user_lastname = request.form['user_lastname']
        user_so_name = request.form['user_so_name']
        user_pass = request.form['user_pass']
        id_admin_role = request.form['id_admin_role']
        user_email = request.form['user_email']

        user_email_exists = User.query.filter_by(user_email=user_email).first()
        user_so_name_exists = User.query.filter_by(user_so_name=user_so_name).first()

        if user_so_name_exists:
            flash("Sign on name already exists", category="error")
        elif user_email_exists:
            flash('Email is already in use.', category='error')
        else:
            new_user = User(
                user_firstname=user_firstname,
                user_lastname=user_lastname,
                user_so_name=user_so_name,
                user_pass=generate_password_hash(user_pass, method='scrypt', salt_length=16),
                id_admin_role=id_admin_role,
                user_email=user_email
            )

            try:
                db.session.add(new_user)
                db.session.commit()
                flash('Admin added successfully', category='success')
                logger.info(f'User {current_user.user_so_name} has created {user_firstname} {user_lastname}')
                return redirect(url_for('admins.user_admin'))
            except IntegrityError as e:
                db.session.rollback()
                logger.error("Duplicate entry user name: %s", e)
                flash('Problem adding candidate: duplicate username', category='danger')
                return redirect(url_for('admins.user_admin'))
    elif request.method == 'POST':
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error in {getattr(form, field).label.text}: {error}", category="error")

    the_admins = User.get_all_admins()
    return render_template('user.html', form=form, admins=the_admins)


@admins.route('/deleteuser/<int:xid>')
def deleteuser(xid):
    """
    Handle user deletion.
    """
    try:
        user_to_delete = User.query.get(xid)
        logger.info(f'User {current_user.user_so_name} is deleting user {user_to_delete.user_firstname} {user_to_delete.user_lastname}')
        db.session.delete(user_to_delete)
        db.session.commit()
        flash('Successfully deleted record', category='success')
    except IntegrityError as e:
        logger.error(f'Error deleting user {user_to_delete}: {e}')
        db.session.rollback()
        flash(f'There was a problem deleting the record: {e}', category='danger')

    return redirect(url_for('admins.user_admin'))