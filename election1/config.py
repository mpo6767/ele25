import os
from datetime import timedelta


class Config:

    SECRET_KEY = 'cvfredsiiisw343434'
    # WTF Form and recaptcha configuration
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 1800  # 30 minutes
    WTF_CSRF_SECRET_KEY = os.getenv('CSRF_SECRET_KEY', '7uhy65tgfr43edsw')
    # Application configuration
    DEBUG = False
    # TESTING = False
    SECRET_KEY = os.getenv('SECRET_KEY', '5thn4ruj88i9')
    # REMEMBER_COOKIE_DURATION = timedelta(minutes=10)
    REMEMBER_COOKIE_DURATION = timedelta(seconds=20)
    SQLALCHEMY_DATABASE_URI = 'sqlite:///election.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # the following home value is used in the demo to redirect to a specific page

    MYTIMEOUT = timedelta(minutes=15)

    URL_HOST = os.getenv('URL_HOST', '127.0.0.1')
    URL_PORT = os.getenv('URL_PORT', '5000')

    # building the home url from the host and port
    HOME = "http://" + URL_HOST + ":" + URL_PORT +"/"




