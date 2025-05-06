import os
from .config import Config  # Import the Config class
import logging.config
from flask import Flask, session
from .models import User
from werkzeug.security import generate_password_hash
from sqlalchemy_utils import database_exists
from sqlalchemy import exc

logging.config.fileConfig('logging.conf')

# create logger
logger = logging.getLogger(__name__)
logger.info('logging is initialized')


def create_app():
    app = Flask(__name__, instance_relative_config=True)

    # application configuration.
    app.config.from_object(Config)  # Load the configuration from config.py

    # configure application extension.
    config_extention(app)

    # configure application blueprints.
    config_blueprint(app)

    return app


def config_blueprint(app):
    """
    Configure and register blueprints with the Flask application.
    """
    from election1.classgrp.view import classgrp
    from election1.admins.view import admins
    from election1.mains.view import mains
    from election1.vote.view import vote
    from election1.dates.view import dates
    from election1.office.view import office
    from election1.candidate.view import candidate
    from election1.misc.view import misc
    from election1.results.view import results
    app.register_blueprint(candidate)
    app.register_blueprint(office)
    app.register_blueprint(admins)
    app.register_blueprint(mains)
    app.register_blueprint(vote)
    app.register_blueprint(classgrp)
    app.register_blueprint(dates)
    app.register_blueprint(misc)
    app.register_blueprint(results)

def config_extention(app):
    """
    Configure application extensions.
    """
    from .extensions import login_manager
    from .extensions import db
    from .extensions import bootstrap
    from .extensions import csrf

    db.init_app(app)
    csrf.init_app(app)

    login_manager.init_app(app)
    config_manager(login_manager)

    if not os.path.exists("instance/election.db"):
        logger.info("database is  not here will be created")

        db_name = "election.db"
        with app.app_context():
            # if database_exists('sqlite:///instance/' + db_name):
            if database_exists(app.config['SQLALCHEMY_DATABASE_URI']):
                logger.info(db_name + " already exists")

            else:
                logger.info(db_name + " does not exist, will create " + db_name)
                try:
                    db.create_all()
                    id_admin_role = 1
                    admin_role_name = "Super Admin"
                    new_admin_role = models.Admin_roles(id_admin_role=id_admin_role,
                                                        admin_role_name=admin_role_name)
                    db.session.add(new_admin_role)

                    id_admin_role = 2
                    admin_role_name = "Election Admin"
                    new_admin_role = models.Admin_roles(id_admin_role=id_admin_role,
                                                        admin_role_name=admin_role_name)
                    db.session.add(new_admin_role)

                    user_firstname = "admin"
                    user_lastname = "admin"
                    user_so_name = "admin"
                    user_pass = "adminpassword"
                    id_admin_role = 1
                    user_email = "no@email.com"
                    user_status = 1
                    user_pw_change = 'N'
                    new_user = User(user_firstname=user_firstname,
                                    user_lastname=user_lastname,
                                    user_so_name=user_so_name,
                                    user_pass=generate_password_hash(user_pass, method='scrypt', salt_length=16),
                                    id_admin_role=id_admin_role,
                                    user_email=user_email,
                                    user_status=user_status,
                                    user_pw_change=user_pw_change)

                    db.session.add(new_user)
                    db.session.commit()

                except exc.SQLAlchemyError as sqlalchemyerror:
                    db.session.rollback()
                    logger.info("got the following SQLAlchemyError: " + str(sqlalchemyerror))
                except Exception as exception:
                    logger.info("got the following Exception: " + str(exception))
                finally:
                    logger.info("db.create_all() in __init__.py was successfull - no exceptions were raised")


def config_manager(manager):
    """
    Configure with Flask-Login manager.
    """
    # from .models import User

    manager.login_message = "You are not logged in to your account."
    # manager.login_view = 'admins.login'
    manager.login_message_category = "info"

    @manager.user_loader
    def user_loader(xid):
        user = User.query.get(int(xid))
        if user is None:
            return None
        return user
