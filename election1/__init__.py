import logging.config
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from election1.config import Config
from election1.ext.csrf import csrf

logging.config.fileConfig('logging.conf')

# create logger
logger=logging.getLogger('simpleExample')
logger.info('logging is initialized')

db = SQLAlchemy()

login_manager = LoginManager()
# login_manager.init_app(election1)
login_manager.login_view = 'admins.login'
login_manager.login_message_category = "info"

# from election1 import controller


def create_app(config_class=Config):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)
    print('secret ' + str(app.secret_key))
    csrf.init_app(app)

    db.init_app(app)
    login_manager.init_app(app)

    from election1.admins.view import admins
    from election1.ballot.view import ballot
    from election1.mains.view import mains
    app.register_blueprint(admins)
    app.register_blueprint(ballot)
    app.register_blueprint(mains)

    from .models import User

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app