from dataclasses import dataclass


@dataclass
class CandidateDataClass:
    id_candidate: int
    firstname: str
    lastname: str
    classgrp_name: str
    office_title: str
    vote_for: int
    nbr_of_votes: int
    winner: bool = False  # Add winner property with default value False

    def __init__(self, id_candidate: int, firstname: str, lastname: str, classgrp_name: str, office_title: str,
                 vote_for: int, nbr_of_votes: int, winner: bool = False):
        self.id_candidate = id_candidate
        self.firstname = firstname
        self.lastname = lastname
        self.classgrp_name = classgrp_name
        self.office_title = office_title
        self.vote_for = vote_for
        self.nbr_of_votes = nbr_of_votes
        self.winner = winner

    @property
    def id_candidate(self):
        return self._id_candidate

    @id_candidate.setter
    def id_candidate(self, value):
        self._id_candidate = value

    @property
    def firstname(self):
        return self._firstname

    @firstname.setter
    def firstname(self, value):
        self._firstname = value

    @property
    def lastname(self):
        return self._lastname

    @lastname.setter
    def lastname(self, value):
        self._lastname = value

    @property
    def classgrp_name(self):
        return self._classgrp_name

    @classgrp_name.setter
    def classgrp_name(self, value):
        self._classgrp_name = value

    @property
    def office_title(self):
        return self._office_title

    @office_title.setter
    def office_title(self, value):
        self._office_title = value

    @property
    def vote_for(self):
        return self._vote_for

    @vote_for.setter
    def vote_for(self, value):
        self._vote_for = value

    @property
    def nbr_of_votes(self):
        return self._nbr_of_votes

    @nbr_of_votes.setter
    def nbr_of_votes(self, value):
        self._nbr_of_votes = value

    @property
    def winner(self):
        return self._winner

    @winner.setter
    def winner(self, value):
        self._winner = value