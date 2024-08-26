from election1.extensions import db
from flask_login import UserMixin
from datetime import datetime
from election1.utils import unique_security_token


class Classgrp(db.Model):
    """
    Represents a class or group in the election system.
    """
    id_classgrp = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(length=45), nullable=False, unique=True)
    sortkey = db.Column(db.Integer, nullable=False, unique=True)
    candidates = db.relationship('Candidate', cascade="all, delete-orphan", backref='classgrp')

class Office(db.Model):
    """
    Represents an office for which candidates can run in the election.
    """
    id_office = db.Column(db.Integer, primary_key=True)
    office_title = db.Column(db.String(length=45), nullable=False, unique=True)
    office_vote_for = db.Column(db.Integer, default=1)
    sortkey = db.Column(db.Integer, nullable=False, unique=True)
    candidates = db.relationship('Candidate', cascade="all, delete-orphan", backref='office')


class Candidate(db.Model):
    """
    Represents a candidate running for an office in a specific class or group.
    """
    id_candidate = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(length=45), nullable=False)
    lastname = db.Column(db.String(length=45), nullable=False)
    id_classgrp = db.Column(db.Integer, db.ForeignKey('classgrp.id_classgrp'), nullable=False)
    id_office = db.Column(db.Integer, db.ForeignKey('office.id_office'), nullable=False)
    votes = db.relationship('Votes', backref='candidate')

class User(db.Model, UserMixin):
    """
    Represents a user in the system, including admin users.
    """
    id_user = db.Column(db.Integer, primary_key=True)
    user_firstname = db.Column(db.String(length=45), nullable=False)
    user_lastname = db.Column(db.String(length=45), nullable=False)
    user_so_name = db.Column(db.String(length=30), nullable=False, unique=True)
    user_pass = db.Column(db.String(256))
    user_email = db.Column(db.String(45), unique=True)
    user_status = db.Column(db.Integer, default=False, nullable=False)
    user_pw_change = db.Column(db.String(length=1))
    user_security = db.Column(db.String(138), default=unique_security_token)
    user_created = db.Column(db.DateTime, default=datetime.now)
    user_sec_send = db.Column(db.DateTime, default=datetime.now)
    id_admin_role = db.Column(db.Integer, db.ForeignKey('admin_roles.id_admin_role'))

    def get_id(self):
        """
        Return the unique identifier for the user.
        """
        return self.id_user


class Admin_roles(db.Model):
    """
    Represents the roles that admin users can have.
    """
    id_admin_role = db.Column(db.Integer, primary_key=True)
    admin_role_name = db.Column(db.String(length=45), nullable=False, unique=True)
    user = db.relationship('User', backref='admin_roles')


class Dates(db.Model):
    """
    Represents the start and end dates for an election.
    """
    iddates = db.Column(db.Integer, primary_key=True)
    start_date_time = db.Column(db.Integer, nullable=False)
    end_date_time = db.Column(db.Integer, nullable=False)


class Votes(db.Model):
    """
    Represents a vote cast by a user.
    """
    id_votes = db.Column(db.Integer, primary_key=True)
    votes_token = db.Column(db.String(138), nullable=False)
    id_candidate = db.Column(db.Integer, db.ForeignKey('candidate.id_candidate'))


class Tokenlist(db.Model):
    """
    Represents a list of tokens used for voting.
    """
    id_tokenlist = db.Column(db.Integer, primary_key=True)
    grp_list = db.Column(db.String(45), nullable=False)
    token = db.Column(db.String(138), nullable=False)
    vote_submitted_date_time = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        """
        Convert the Tokenlist object into a dictionary format.
        """
        return {
            'id_tokenlist': self.id_tokenlist,
            'grp_list': self.grp_list,
            'token': self.token,
            'vote_submitted_date_time': self.vote_submitted_date_time.isoformat() if self.vote_submitted_date_time else None
        }