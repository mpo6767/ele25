from election1 import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy.sql import func

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Classgrp(db.Model):
    id_classgrp = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(length=45), nullable=False,unique=True)
    sortkey = db.Column(db.Integer, nullable=False, unique=True)
    candidates = db.relationship('Candidate', backref='classgrp')


class Office(db.Model):
    id_office = db.Column(db.Integer, primary_key=True)
    office_title = db.Column(db.String(length=45), nullable=False, unique=True)
    sortkey = db.Column(db.Integer, nullable=False, unique=True)
    candidates = db.relationship('Candidate', backref='office')


class Candidate(db.Model):
    id_candidate = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(length=45), nullable=False)
    lastname = db.Column(db.String(length=45), nullable=False)
    id_classgrp = db.Column(db.Integer, db.ForeignKey('classgrp.id_classgrp'))
    id_office = db.Column(db.Integer, db.ForeignKey('office.id_office'))


class User(db.Model, UserMixin):
    id_user = db.Column(db.Integer, primary_key=True)
    user_firstname = db.Column(db.String(length=45), nullable=False)
    user_lastname = db.Column(db.String(length=45), nullable=False)
    user_so_name = db.Column(db.String(length=12), nullable=False, unique=True)
    user_pass = db.Column(db.String(150))
    user_role = db.Column(db.String(1), nullable=False)
    user_email = db.Column(db.String(45), unique=True)
    id_admin_role = db.Column(db.Integer, db.ForeignKey('admin_roles.id_admin_role'))

    def get_id(self):
        return (self.id_user)

    # @property
    # def password(self):
    #     raise AttributeError('password not')
    #
    # @password.setter
    # def password(self, password):
    #     self.user_pass = generate_password_hash(password)
    #
    # def verify_password(self, password):
    #     return check_password_hash(self.user_pass, password)


class Admin_roles(db.Model):
    id_admin_role = db.Column(db.Integer, primary_key=True)
    admin_role_name = db.Column(db.String(length=45), nullable=False, unique=True)
    user = db.relationship('User', backref='admin_roles')


class Dates(db.Model):
    iddates = db.Column(db.Integer, primary_key=True)
    start_date_time = db.Column(db.DateTime, nullable=False)
    end_date_time = db.Column(db.DateTime, nullable=False)

