# -*- coding: utf-8 -*-
from datetime import datetime
from flask.ext.sqlalchemy import SQLAlchemy

from healthtracker import app
from healthtracker.utils import random_string
from healthtracker.security import encrypt_password, verify_password



db = SQLAlchemy(app)


patient_questions = db.Table('patient_questions',
                             db.Column('patient_id', db.Integer, db.ForeignKey('patients.id')),
                             db.Column('question_id', db.Integer, db.ForeignKey('questions.id')))


class Patient(db.Model):
    __tablename__ = "patients"
    id = db.Column(db.Integer, db.Sequence('patients_id_seq'), primary_key=True)
    email = db.Column(db.Text, unique=True)
    name = db.Column(db.Text)

    encrypted_password = db.Column(db.Text)

    created_at = db.Column(db.DateTime(timezone=True),
                           default=datetime.utcnow)

    provider_id = db.Column(db.Integer, db.ForeignKey("providers.id"))

    statuses = db.relationship("Status",
                               backref="patients",
                               lazy="dynamic")
    demographics = db.relationship("Demographics",
                                   backref="patients",
                                   uselist=False)
    questions = db.relationship("Question", secondary=patient_questions,
                                backref=db.backref("patients", lazy="dynamic"))

    def __init__(self, email=None, name=None, provider=None, password=None):
        if None in (email, name, provider, password): raise Exception("Needs all params") # TK this is crap; do this right.
        self.email = email
        self.name = name
        self.provider_id = provider.id
        self.encrypted_password = encrypt_password(password)

    def __repr__(self):
        return "<Patient('%s' :: '%s')>" % (self.name, self.email)

    @staticmethod
    def find_by(**kwargs):
        return Patient.query.filter_by(**kwargs).first()

    @staticmethod
    def authenticate(email=None, guessed_password=None):
        patient = User.find_by(email=email)
        return verify_password(patient.encrypted_password,
                               guessed_password)


class Organization(db.Model):
    __tablename__ = "organizations"
    id = db.Column(db.Integer, db.Sequence('organizations_id_seq'), primary_key=True)
    name = db.Column(db.Text)

    providers = db.relationship("Provider", backref="organizations", lazy="dynamic")

    def __init__(self, name=None):
        self.name = name

    def __repr__(self):
        return "<Organization('%s')>" % (self.name)


class Provider(db.Model):
    __tablename__ = "providers"
    id = db.Column(db.Integer, db.Sequence('providers_id_seq'), primary_key=True)
    
    name = db.Column(db.Text)
    username = db.Column(db.Text)
    email = db.Column(db.Text)
    encrypted_password = db.Column(db.Text)

    organization_id = db.Column(db.Integer, db.ForeignKey("organizations.id"))

    created_at = db.Column(db.DateTime(timezone=True),
                           default=datetime.utcnow)

    patients = db.relationship("Patient", backref="providers", lazy="dynamic")

    def __init__(self, email=None, name=None, username=None, password=None, organization_id=organization_id):
        if None in (email, name, username, password): raise Exception("Needs all params") # TK this is crap; do this right.
        self.email = email
        self.name = name
        self.username = username
        self.encrypted_password = encrypt_password(password)
        self.organization_id = organization_id

    def __repr__(self):
        return "<Provider('%s' :: '%s')>" % (self.name, self.username)


class Question(db.Model):
    __tablename__ = "questions"
    id = db.Column(db.Integer, db.Sequence('questions_id_seq'), primary_key=True)
    name = db.Column(db.Text)
    view_name = db.Column(db.Text)
    
    def __init__(self, name=None, view_name=None):
        self.name = name
        self.view_name = view_name

    def __repr__(self):
        return "<Question('%s' :: '%s')>" % (self.name, self.view_name)


class Answer(db.Model):
    __tablename__ = "answers"
    id = db.Column(db.Integer, db.Sequence('answers_id_seq'), primary_key=True)
    value = db.Column(db.Text)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"))
    question_id = db.Column(db.Integer, db.ForeignKey("questions.id"))
    status_id = db.Column(db.Integer, db.ForeignKey("statuses.id"))

    question = db.relationship("Question",
                               backref=db.backref("answers", lazy="dynamic"))
    
    def __init__(self, question=None, patient=None, value=None):
        self.question_id = question.id
        self.patient_id = patient.id
        self.value = value

    def __repr__(self):
        return "<Answer('%s' :: '%s')>" % (self.question.name, self.value) 


class Status(db.Model):
    __tablename__ = "statuses"
    id = db.Column(db.Integer, db.Sequence('statuses_id_seq'), primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"))

    created_at = db.Column(db.DateTime(timezone=True),
                           default=datetime.utcnow)
    
    answers = db.relationship("Answer",
                               backref="statuses",
                               lazy="dynamic")

    def __init__(self, patient=None):
        self.patient_id = patient.id

    def __repr__(self):
        return "<Status('%s')>" % (self.patient.email)


class Demographics(db.Model):
    __tablename__ = "demographics"
    id = db.Column(db.Integer, db.Sequence('demographics_id_seq'), primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"))

    dob = db.Column(db.DateTime())
    sex = db.Column(db.String(8))

    created_at = db.Column(db.DateTime(timezone=True),
                           default=datetime.utcnow)

    def __init__(self, user=None, dob=None, sex=None):
        self.user_id = user.id

    def __repr__(self):
        return "<Demographics('%s':: '%s','%s')>" % (self.patient.name,
                                                     str(self.dob),
                                                     self.sex)
