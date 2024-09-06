import secrets

from flask_login import current_user


def unique_security_token():
    return str(secrets.token_hex())


def get_token():
    return str(secrets.token_hex())


def is_user_authenticated():
    return current_user.is_authenticated

