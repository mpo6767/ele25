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
    creation_datetime = db.Column(db.DateTime, default=datetime.now, nullable=False)
    candidates = db.relationship('Candidate', cascade="all, delete-orphan", backref='classgrp')


    @classmethod
    def classgrp_query(cls):
        return [(c.id_classgrp, c.name) for c in cls.query.order_by(cls.sortkey).all()]


class Office(db.Model):
    """
    Represents an office for which candidates can run in the election.
    """
    id_office = db.Column(db.Integer, primary_key=True)
    office_title = db.Column(db.String(length=45), nullable=False, unique=True)
    office_vote_for = db.Column(db.Integer, default=1, nullable=False)
    sortkey = db.Column(db.Integer, nullable=False, unique=True)
    creation_datetime = db.Column(db.DateTime, default=datetime.now, nullable=False)
    candidates = db.relationship('Candidate', cascade="all, delete-orphan", backref='office')

    @classmethod
    def office_query(cls):
        return[(o.id_office, o.office_title) for o in cls.query.order_by(cls.sortkey).all()]

    @classmethod
    def query_offices_for_classgroup_with_details_as_list(cls, classgroup_name):
        offices = db.session.query(
            cls.office_title,
            cls.sortkey,
            cls.office_vote_for
        ).join(Candidate).join(Classgrp).filter(
            Classgrp.name == classgroup_name
        ).distinct().order_by(cls.sortkey).all()

        return [[office.office_title, office.sortkey, office.office_vote_for] for office in offices]

class Candidate(db.Model):
    """
    Represents a candidate running for an office in a specific class or group.
    """
    id_candidate = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(length=45), nullable=False)
    lastname = db.Column(db.String(length=45), nullable=False)
    creation_datetime = db.Column(db.DateTime, default=datetime.now, nullable=False)
    id_classgrp = db.Column(db.Integer, db.ForeignKey('classgrp.id_classgrp'), nullable=False)
    id_office = db.Column(db.Integer, db.ForeignKey('office.id_office'), nullable=False)
    votes = db.relationship('Votes', backref='candidate')

    @classmethod
    def get_candidates_for_specific_office_by_classgrp(cls, choices_classgrp, choices_office):
        return db.session.query(cls, Classgrp, Office).select_from(cls).join(Classgrp).join(
            Office).filter(Classgrp.id_classgrp == choices_classgrp, Office.id_office == choices_office)

    @classmethod
    def get_candidates_for_all_offices_by_classgrp(cls, choices_classgrp):
        return db.session.query(cls, Classgrp, Office).select_from(cls).join(Classgrp).join(
            Office).filter(Classgrp.id_classgrp == choices_classgrp)

    @classmethod
    def candidate_search(cls, group):
        return db.session.query(cls, Classgrp, Office).select_from(cls).join(Classgrp).join(
            Office).order_by(Classgrp.sortkey, Office.sortkey).where(Classgrp.id_classgrp == group)

    @classmethod
    def check_and_insert_writein_candidate(cls, choices_classgrp, choices_office):
        existing_candidate = cls.query.filter_by(
            firstname="Writein",
            lastname="Candidate",
            id_classgrp=choices_classgrp,
            id_office=choices_office
        ).first()

        if not existing_candidate:
            new_candidate = cls(
                firstname="Writein",
                lastname="Candidate",
                id_classgrp=choices_classgrp,
                id_office=choices_office
            )
            db.session.add(new_candidate)

    @classmethod
    def check_writein_candidate(cls, id_classgrp, id_office):
        return cls.query.filter_by(
            firstname='Writein',
            id_classgrp=id_classgrp,
            id_office=id_office
        ).first() is not None

    @classmethod
    def get_candidates_by_classgrp(cls, classgrp_id):
        return db.session.query(
            cls,
            Classgrp.name.label('classgrp_name'),
            Office.office_title.label('office_title')
        ).join(Classgrp).join(Office).filter(cls.id_classgrp == classgrp_id).order_by(Classgrp.sortkey, Office.sortkey).all()


    @classmethod
    def check_existing_candidate(cls, firstname, lastname, id_classgrp):
        return cls.query.filter_by(
            firstname=firstname,
            lastname=lastname,
            id_classgrp=id_classgrp
        ).first() is not None

    @classmethod
    def get_candidates_by_office(cls, office_id):
        return db.session.query(cls).filter_by(id_office=office_id).all()



class User(db.Model, UserMixin):
    """
    Represents a user in the system, including admin users.
    """
    id_user = db.Column(db.Integer, primary_key=True)
    user_firstname = db.Column(db.String(length=45), nullable=False)
    user_lastname = db.Column(db.String(length=45), nullable=False)
    user_so_name = db.Column(db.String(length=30), nullable=False, unique=True)
    user_pass = db.Column(db.String(length=256))
    user_email = db.Column(db.String(length=45), unique=True)
    user_status = db.Column(db.Integer, default=False, nullable=False)
    user_pw_change = db.Column(db.String(length=1))
    user_security = db.Column(db.String(138), default=unique_security_token)
    user_created = db.Column(db.DateTime, default=datetime.now)
    user_sec_send = db.Column(db.DateTime, default=datetime.now)
    user_creation_datetime = db.Column(db.DateTime, default=datetime.now, nullable=False)
    id_admin_role = db.Column(db.Integer, db.ForeignKey('admin_roles.id_admin_role'))

    def get_id(self):
        """
        Return the unique identifier for the user.
        """
        return self.id_user

    @classmethod
    def get_all_admins(cls):
        return db.session.query(cls, Admin_roles).select_from(cls).join(Admin_roles).order_by()

    @classmethod
    def get_user_by_so_name(cls, so_name):
        return cls.query.filter_by(user_so_name=so_name).first()


class Admin_roles(db.Model):
    """
    Represents the roles that admin users can have.
    """
    id_admin_role = db.Column(db.Integer, primary_key=True)
    admin_role_name = db.Column(db.String(length=45), nullable=False, unique=True)
    creation_datetime = db.Column(db.DateTime, default=datetime.now, nullable=False)
    user = db.relationship('User', backref='admin_roles')


class Dates(db.Model):
    """
    Represents the start and end dates for an election.
    """
    iddates = db.Column(db.Integer, primary_key=True)
    start_date_time = db.Column(db.Integer, nullable=False)
    end_date_time = db.Column(db.Integer, nullable=False)
    creation_datetime = db.Column(db.DateTime, default=datetime.now, nullable=False)

    @classmethod
    def after_start_date(cls):
        date = cls.query.first()
        if date:
            start_date_time = datetime.fromtimestamp(date.start_date_time)
            current_date_time = datetime.now()
            return current_date_time > start_date_time
        return False

    @classmethod
    def check_dates(cls):
        date = cls.query.first()
        return date is not None


class Votes(db.Model):
    """
    Represents a vote cast by a user.
    If there is a write-in candidate, the write-in candidate will be store
    in the votes_writein_name field.
    """
    id_votes = db.Column(db.Integer, primary_key=True)
    votes_token = db.Column(db.String(138), nullable=False)
    votes_writein_name = db.Column(db.String(45), nullable=True)
    creation_datetime = db.Column(db.DateTime, default=datetime.now, nullable=False)
    id_candidate = db.Column(db.Integer, db.ForeignKey('candidate.id_candidate'))


class WriteinCandidate(db.Model):
    """
    Represents a write-in candidate.
    The write-in candidate nust be registered by an admin user.
    """
    id_writein_candidate = db.Column(db.Integer, primary_key=True)
    writein_candidate_name = db.Column(db.String(45), nullable=False)
    creation_datetime = db.Column(db.DateTime, default=datetime.now, nullable=False)
    id_office = db.Column(db.Integer, db.ForeignKey('office.id_office'))
    id_classgrp = db.Column(db.Integer, db.ForeignKey('classgrp.id_classgrp'))

    @classmethod
    def get_writein_candidates_sorted(cls):
        return db.session.query(cls, Classgrp, Office).select_from(cls).join(Classgrp).join(
            Office).order_by(Classgrp.sortkey, Office.sortkey).all()

    @classmethod
    def check_existing_writein_candidate(cls, writein_candidate_name, id_classgrp, id_office):
        return cls.query.filter_by(
            writein_candidate_name=writein_candidate_name,
            id_classgrp=id_classgrp,
            id_office=id_office
        ).first() is not None


class Tokenlist(db.Model):
    """
    Represents a list of tokens used for voting.
    """
    id_tokenlist = db.Column(db.Integer, primary_key=True)
    grp_list = db.Column(db.String(45), nullable=False)
    token = db.Column(db.String(138), nullable=False)
    vote_submitted_date_time = db.Column(db.DateTime, nullable=True)
    creation_datetime = db.Column(db.DateTime, default=datetime.now, nullable=False)



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

    @classmethod
    def get_tokenlist_record(cls, token):
        """
        Retrieve a Tokenlist record if the given token exists in the Tokenlist.
        :param token: The token to search for in the Tokenlist.
        :return: The Tokenlist record as a dictionary .
         """
        token_record = cls.query.filter_by(token=token).first()

        if token_record is None:
            # Token does not exist
            return {'error': 'Invalid token'}
        if token_record.vote_submitted_date_time is not None:
            # Token exists but vote has been submitted
            return {'error': 'Token has already been used'}
        return token_record.to_dict()