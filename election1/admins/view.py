from flask import Blueprint,request, current_app, redirect, flash, render_template,url_for
from election1.admins.form import UserForm,LoginForm,DatesForm
from election1.extensions import db
from ..models import (User, Admin_roles, Dates)
from sqlalchemy.exc import IntegrityError
# from flask_login import login_user, logout_user, login_required
import logging
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user

admins = Blueprint('admins', __name__)

@admins.route('/user_admin',methods=['GET', 'POST'])
def user_admin():
    form = UserForm()
    if form.validate():
        if request.method == 'POST':
            print("1")
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
                new_user = User(user_firstname=user_firstname,
                                user_lastname = user_lastname,
                                user_so_name = user_so_name,
                                user_pass=generate_password_hash(user_pass,method='scrypt', salt_length=16),
                                id_admin_role = id_admin_role,
                                user_email = user_email)
                try:
                    print("2")
                    db.session.add(new_user)
                    db.session.commit()
                    flash('candidate added successfully',category='success')
                    return redirect(url_for('admins.user_admin'))
                except IntegrityError as e:
                    print("3")
                    db.session.rollback()
                    logging.error("Duplicate entry user name: %s", e)
                    flash('problem adding candidate duplicate username', category='danger')
                    return redirect(url_for('admins.user_admin'))
    print("4")
    admins = db.session.query(User, Admin_roles).select_from(User).join(Admin_roles).order_by()
    return render_template('user.html', form=form,admins=admins)

@admins.route('/login',methods=('GET', 'POST'))
def login():
    form = LoginForm()
    # if request.method == 'POST':
    if form.validate_on_submit():
        print(' validate true')
        login_so_name = request.form.get("login_so_name")
        login_pass = request.form.get("login_pass")
        print(login_pass)
        print(generate_password_hash(login_pass,method='scrypt', salt_length=16))

        user_so_name_exists = User.query.filter_by(user_so_name=login_so_name).first()
        print('user.user_pass')
        if user_so_name_exists:
            user = User.query.filter_by(user_so_name=login_so_name).first()
            print(user.user_pass)
            if check_password_hash(user.user_pass, login_pass ):
                flash("Logged in!", category='success')
                login_user(user, remember=True)
                return redirect(url_for('mains.homepage'))
            else:
                flash('Password is incorrect.', category='error')
        else:
            flash('sign on name does not exist.', category='error')
    return render_template('login.html', form=form)


@admins.route('/deleteuser/<int:id>')
def deleteuser(id):
    user_to_delete = User.query.get_or_404(id)
    print(user_to_delete)
    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash('successfully deleted record')
        return redirect(url_for('admins.user_admin'))
    except:
        db.session.rollback()
        flash('There was a problem deleting record')
        return redirect(url_for('admins.user_admin'))


@admins.route('/dates', methods=['GET','POST'])
def dates():
    form = DatesForm()
    if form.validate_on_submit():
        start_date_time = request.form.get('start_date_time')
        end_date_time = request.form.get('end_date_time')
        new_dates = Dates(start_date_time=start_date_time,end_date_time=end_date_time)

        print("2")
        db.session.add(new_dates)
        db.session.commit()
        return redirect(url_for('mains.homepage'))

    return render_template('dates.html', form=form)