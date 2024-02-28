import os
import secrets
class Config:
    db_user = os.environ.get('DB_USER')
    db_pass = os.environ.get('DB_PASS')

    SQLALCHEMY_DATABASE_URI = ('mysql+pymysql://' + str(db_user) + ':' +
                               str(db_pass) + '@localhost/school_db')
    SECRET_KEY = 'cvfredssw343434'
