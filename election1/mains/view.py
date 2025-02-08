from datetime import datetime

from flask import render_template, request, Blueprint, redirect, url_for, flash, session, current_app
from flask_wtf.csrf import generate_csrf
from werkzeug.security import check_password_hash

from election1 import logger, User
from election1.admins.form import LoginForm
from flask_login import login_user, logout_user, login_required, current_user

mains = Blueprint('mains', __name__)

@mains.route('/', methods=['GET'])
def index():
    print("Entered index")
    """
    Redirect to homepage.
    """
    if current_user.is_authenticated:
        logout_user()

    return redirect(url_for('mains.homepage'))


@mains.route('/home', methods=['GET'])
@mains.route('/homepage', methods=['GET'])
def homepage():

    logger.info("Entered homepage")
    return render_template('homepage.html')


@mains.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handle user login.
    """
    logger.info("Entered Login")
    form = LoginForm()
    if current_user.is_authenticated:
        print("User is already authenticated")
        return redirect(url_for('mains.homepage'))

    if form.validate_on_submit():
        login_so_name = request.form.get("login_so_name")
        login_pass = request.form.get("login_pass")
        user = User.get_user_by_so_name(login_so_name)

        if user and check_password_hash(user.user_pass, login_pass):
            login_user(user)
            logger.info(f'User {current_user.user_so_name} has logged on')

            # Generate and set a new CSRF token
            new_csrf_token = generate_csrf()
            session['csrf_token'] = new_csrf_token
            print(f'New CSRF token: {new_csrf_token}')

            return redirect(url_for('mains.homepage'))
        else:
            flash('Invalid username or password.', category='error')

    current_date_time = datetime.now()
    session['last_activity'] = current_date_time.strftime("%Y-%m-%d %H:%M:%S")

    the_timeout = current_app.config['MYTIMEOUT']
    the_timeout_minutes = int(the_timeout.total_seconds() / 60)

    return render_template('login.html', the_timeout=the_timeout_minutes, form=form)

@mains.route('/logout' )
@login_required
def logout():
    """
    Handle user logout.
    """
    logger.info(f'User {current_user.user_so_name} has logged out')
    logout_user()
    return redirect(url_for('mains.homepage'))
