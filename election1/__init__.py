import logging
import logging.config
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

logging.config.fileConfig('logging.conf')

# create logger
logger=logging.getLogger('simpleExample')
logger.info('logging is initialized')

app = Flask(__name__, instance_relative_config=True)

db_user = os.environ.get('DB_USER')
db_pass = os.environ.get('DB_PASS')

# connection_string = "mysql+mysqlconnector://root:myB34tl3B41lysql@localhost:3306/sample_db"
# engine = create_engine(connection_string, echo=True)
# with engine.connect() as connection:
#     result = connection.execute(text("SELECT * FROM sample_db.candidate"))

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://' + str(db_user) + ':' + str(db_pass) + '@localhost/school_db'

app.config['SECRET_KEY'] = 'ec9439cfc6c796ae2029594d'

db = SQLAlchemy(app)

login_manager = LoginManager(app)
# login_manager.init_app(election1)
login_manager.login_view = 'login'
login_manager.login_message_category = "info"



from election1 import controller
