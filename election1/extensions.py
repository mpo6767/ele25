from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap


# A bootstrap5 class for styling client side.
bootstrap = Bootstrap()

# database for managing user data.
db = SQLAlchemy()

# login manager for managing user authentication.
login_manager = LoginManager()