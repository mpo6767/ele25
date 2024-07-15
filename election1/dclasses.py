from dataclasses import dataclass


@dataclass
class CandidateDataClass:
    id_candidate: int
    firstname: str
    lastname: str
    classgrp_name: str
    office_title: str
    vote_for: int
    # nbr_of_votes: int

    def __init__(self, id_candidate: int, firstname: str, lastname: str, classgrp_name: str, office_title: str,
                 vote_for: int, nbr_of_votes: int):
        self.id_candidate = id_candidate
        self.firstname = firstname
        self.lastname = lastname
        self.classgrp_name = classgrp_name
        self.office_title = office_title
        self.vote_for = vote_for
        self.nbr_of_votes = nbr_of_votes

    @property
    def id_candidate(self):
        return self.id_candidate

    @property
    def firstname(self):
        return self.firstname

    @property
    def lastname(self):
        return self.lastname

    @property
    def classgrp_name(self):
        return self.classgrp_name

    @property
    def office_title(self):
        return self.office_title

    @property
    def vote_for(self):
        return self.vote_for

    @property
    def nbr_of_votes(self):
        return self.nbr_of_votes

    @vote_for.setter
    def vote_for(self, value):
        self._vote_for = value

    @nbr_of_votes.setter
    def nbr_of_votes(self, value):
        self._nbr_of_votes = value

    @id_candidate.setter
    def id_candidate(self, value):
        self._id_candidate = value

    @firstname.setter
    def firstname(self, value):
        self._firstname = value

    @lastname.setter
    def lastname(self, value):
        self._lastname = value

    @classgrp_name.setter
    def classgrp_name(self, value):
        self._classgrp_name = value

    @office_title.setter
    def office_title(self, value):
        self._office_title = value
