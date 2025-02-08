import secrets

from datetime import datetime
from flask import session, current_app
from flask_login import current_user


def unique_security_token():
    return str(secrets.token_hex())


def get_token():
    return str(secrets.token_hex())


def is_user_authenticated():
    return current_user.is_authenticated

def session_check():
    session.permanent = True
    idle_timeout = current_app.config['MYTIMEOUT'].total_seconds()
    session.modified = True
    # Get the current date and time
    current_date_time = datetime.now()

    if 'last_activity' in session:
        now = datetime.now()
        last_activity = datetime.strptime(session['last_activity'], "%Y-%m-%d %H:%M:%S")
        time_difference = now - last_activity
        time_difference_in_seconds = time_difference.total_seconds()
        if time_difference_in_seconds > idle_timeout:
            session.clear()
            # home = current_app.config['HOME']
            # error = 'idle timeout '
            # # return render_template('bad_token.html' error=error, home=home)
            return False
    session['last_activity'] = current_date_time.strftime("%Y-%m-%d %H:%M:%S")
    return True

