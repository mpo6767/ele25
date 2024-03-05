import os
import logging.config
from flask import Flask
from .models import User
from werkzeug.security import generate_password_hash
from sqlalchemy_utils import database_exists
from election1.config import Config
from sqlalchemy import  exc
from datetime import timedelta

logging.config.fileConfig('logging.conf')

# create logger
logger=logging.getLogger('simpleExample')
logger.info('logging is initialized')

# db = SQLAlchemy()

# login_manager = LoginManager()
# login_manager.init_app(election1)


# from election1 import controller


def create_app(config_class=Config):

    app = Flask(__name__, instance_relative_config=True)

    # application configuration.
    config_application(app)
    # configure application extension.
    config_extention(app)
    # configure application blueprints.
    config_blueprint(app)




    # app.config.from_object(Config)
    # print('secret ' + str(app.secret_key))

    # csrf.init_app(app)
    # db.init_app(app)

    # login_manager.init_app(app)

    # from election1.admins.view import admins
    # from election1.ballot.view import ballot
    # from election1.mains.view import mains
    # app.register_blueprint(admins)
    # app.register_blueprint(ballot)
    # app.register_blueprint(mains)

    # from .models import User

    # @login_manager.user_loader
    # def load_user(id):
    #     return User.query.get(int(id))

    return app

def config_application(app):
    # Application configuration
    app.config["DEBUG"] = False
    app.config["TESTING"] = False
    app.config["SECRET_KEY"] = os.getenv('SECRET_KEY', '5thn4ruj88i9')
    app.config["BOOTSTRAP_BOOTSWATCH_THEME"] = 'Pulse'
    app.config["REMEMBER_COOKIE_DURATION"] = timedelta(seconds=20)

    # WTF Form and recaptcha configuration
    app.config["WTF_CSRF_SECRET_KEY"] = os.getenv('CSRF_SECRET_KEY', '7uhy65tgfr43edsw')
    app.config["WTF_CSRF_ENABLED"] = True
    app.config["RECAPTCHA_PUBLIC_KEY"] = os.getenv('PUBLIC_KEY', None)
    app.config["RECAPTCHA_PRIVATE_KEY"] = os.getenv('RECAPTCHA_KEY', None)

    # SQLAlchemy configuration
    # db_user = os.environ.get('DB_USER')
    # db_pass = os.environ.get('DB_PASS')
    # app.config["SQLALCHEMY_DATABASE_URI"] =('mysql+pymysql://' + str(db_user) + ':' +
    #                            str(db_pass) + '@localhost/school_db')

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///election.db'

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Flask-Mail configuration
    app.config["MAIL_SERVER"] = os.getenv('MAIL_SERVER', 'smtp.office365.com')
    app.config["MAIL_PORT"] = 587
    app.config["MAIL_USE_TLS"] = True
    app.config["MAIL_USERNAME"] = os.getenv('MAIL_USERNAME', 'michael@cpo2llc.com')
    app.config["MAIL_PASSWORD"] = os.getenv('MAIL_PASSWORD', 'T0mP3tty')


def config_blueprint(app):
    """
    Configure and register blueprints with the Flask application.
    """
    from election1.admins.view import admins
    from election1.ballot.view import ballot
    from election1.mains.view import mains
    app.register_blueprint(admins)
    app.register_blueprint(ballot)
    app.register_blueprint(mains)

def config_extention(app):
    """
    Configure application extensions.
    """
    from .extensions import login_manager
    from .extensions import db
    from .extensions import bootstrap
    from .extensions import csrf

    db.init_app(app)

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

    login_manager.init_app(app)
    config_manager(login_manager)
    csrf.init_app(app)



def config_manager(manager):
    """
    Configure with Flask-Login manager.
    """
    from .models import User

    manager.login_message = "You are not logged in to your account."
    manager.login_view = 'admins.login'
    manager.login_message_category = "info"


    @manager.user_loader
    def user_loader(id):
        return User.query.get_or_404(id)
