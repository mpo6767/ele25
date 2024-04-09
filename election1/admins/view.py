from flask import Blueprint, request, redirect, flash, render_template, url_for
from election1.admins.form import UserForm, LoginForm
from election1.extensions import db
from election1.models import (User, Admin_roles)
from sqlalchemy.exc import IntegrityError
# from flask_login import login_user, logout_user, login_required
import logging
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user

admins = Blueprint('admins', __name__)


@admins.route('/user_admin', methods=['GET', 'POST'])
def user_admin():
    form = UserForm()
    if form.validate():
        if request.method == 'POST':
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
                new_user = User()
                new_user.user_firstname = user_firstname
                new_user.user_lastname = user_lastname
                new_user.user_so_name = user_so_name
                new_user.user_pass = generate_password_hash(user_pass, method='scrypt', salt_length=16)
                new_user.id_admin_role = id_admin_role
                new_user.user_email = user_email

                try:
                    db.session.add(new_user)
                    db.session.commit()
                    flash('candidate added successfully', category='success')
                    return redirect(url_for('admins.user_admin'))
                except IntegrityError as e:
                    db.session.rollback()
                    logging.error("Duplicate entry user name: %s", e)
                    flash('problem adding candidate duplicate username', category='danger')
                    return redirect(url_for('admins.user_admin'))
    the_admins = db.session.query(User, Admin_roles).select_from(User).join(Admin_roles).order_by()
    return render_template('user.html', form=form, admins=the_admins)


@admins.route('/login', methods=('GET', 'POST'))
def login():
    form = LoginForm()
    if current_user.is_authenticated:
        return redirect(url_for('mains.homepage'))

    # if request.method == 'POST':
    if form.validate_on_submit():
        login_so_name = request.form.get("login_so_name")
        login_pass = request.form.get("login_pass")
        user_so_name_exists = User.query.filter_by(user_so_name=login_so_name).first()
        if user_so_name_exists:
            user = User.query.filter_by(user_so_name=login_so_name).first()
            if check_password_hash(user.user_pass, login_pass):
                login_user(user)
                logging.info('user ' + str(current_user.user_so_name) + ' has logged on')
                return redirect(url_for('mains.homepage'))
            else:
                flash('Password is incorrect.', category='error')
        else:
            flash('sign on name does not exist.', category='error')
    return render_template('login.html', form=form)


@admins.route('/logout', strict_slashes=False)
@login_required
def logout():
    logout_user()

    return redirect(url_for('mains.homepage'))


@admins.route('/deleteuser/<int:id>')
def deleteuser(id):
    user_to_delete = User()
    try:
        user_to_delete = User.query.get(id)
        logging.info('deleting user ' + str(user_to_delete))
        db.session.delete(user_to_delete)
        db.session.commit()
        flash('successfully deleted record')
        return redirect(url_for('admins.user_admin'))
    except Exception as e:
        logging.info('deleting user ' + str(user_to_delete))
        db.session.rollback()
        flash('There was a problem deleting record')
        return redirect(url_for('admins.user_admin'))
