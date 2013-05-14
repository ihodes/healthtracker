# -*- coding: utf-8 -*-
from datetime import datetime

from .utils import random_string
from .extensions import db
from sqlalchemy.ext.associationproxy import association_proxy


class ScheduledQuestion(db.Model):
    __tablename__ = 'scheduled_questions'
    id = db.Column(db.Integer, db.Sequence('scheduled_questions_id_seq'), primary_key=True)
    user_id = db.Column('user_id', db.Integer, db.ForeignKey('users.id'))
    question_id = db.Column('question_id', db.Integer, db.ForeignKey('questions.id'))
    scheduled_for = db.Column('scheduled_for', db.DateTime(timezone=True))
    notification_method = db.Column('notification_method', db.String(255))

    question = db.relationship('Question', backref=db.backref('scheduling_user_assocs', lazy='dynamic'))
    user = db.relationship('User', backref='scheduled_question_assocs')
    
    def __init__(self, user, question, notification_method=None):
        self.user_id = user.id
        self.question_id = question.id
        self.notification_method = notification_method or 'none'
        

class Answer(db.Model):
    __tablename__ = "answers"
    id = db.Column(db.Integer, db.Sequence('answers_id_seq'), primary_key=True)
    value = db.Column(db.Text)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    question_id = db.Column(db.Integer, db.ForeignKey("questions.id"))
    question = db.relationship("Question", backref=db.backref('answers', lazy='dynamic'))

    created_at = db.Column(db.DateTime(timezone=True),
                           default=datetime.utcnow)

    def __init__(self, user, question, value):
        self.user_id = user.id
        self.question_id = question.id
        self.value = value

    def __repr__(self):
        return "<Answer({}::{}::{})>".format(self.user.email,
                                             self.value,
                                             self.question.name)


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, db.Sequence('users_id_seq'), primary_key=True)
    email = db.Column(db.String(255), unique=True)
    auth_token = db.Column(db.String, unique=True)
    answers = db.relationship("Answer", backref="user", lazy="dynamic")
    is_confirmed = db.Column(db.Boolean, default=False)
    is_approved = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)

    name = db.Column(db.Text)
    notes = db.Column(db.Text)
    timezone = db.Column(db.String(255))

    scheduled_questions = db.relationship('ScheduledQuestion',  backref='users')
    questions = association_proxy('scheduled_questions', 'question')


    def __init__(self, email, is_approved=False):
        self.email = email
        self.auth_token = random_string(36)
        self.is_approved = is_approved

    def __repr__(self):
        return "<User('%s')>" % (self.email)

    def reset_auth_token(self):
        self.auth_token = random_string(36)
        self.save()

    def confirm(self):
        self.is_confirmed = True
        self.save()

    def unconfirm(self):
        self.is_confirmed = False
        self.save()

    def approve(self):
        self.is_approved = True
        self.save()

    def unapprove(self):
        self.is_approved = False
        self.save()

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    # hack for now
    def wq(self):
        return sum(map(lambda a: float(a.value), self.answers.order_by('created_at ASC').all()[-7:]))/7

    # hack for now
    def last_30_days_str(self):
        return str(map(lambda a: int(a.value), self.answers.order_by('created_at ASC').all()[-30:]))[1:-1]

    @staticmethod
    def create(email):
        if User.query.filter_by(email=email).first() is None:
            user = User(email)
            user.questions.append(Question.default())
            user.save()
            return user
        return None

    @staticmethod
    def find_by(**kwargs):
        return User.query.filter_by(**kwargs).first()


class Question(db.Model):
    __tablename__ = "questions"
    id = db.Column(db.Integer, db.Sequence('questions_id_seq'), primary_key=True)
    name = db.Column(db.String(255), unique=True)
    text = db.Column(db.Text)

    is_default = db.Column(db.Boolean, default=False)

    min_value = db.Column(db.Integer, default=0)
    max_value = db.Column(db.Integer, default=5)

    def __init__(self, name, text, min_value=0, max_value=5):
        self.name = name
        self.text = text
        # well, this is hacky. TK fix with WTForms?
        self.min_value = 0 if min_value == '' else int(min_value)
        self.max_value = 5 if max_value == '' else int(max_value)

    def __repr__(self):
        return "<Question::{}>".format(self.name)

    @classmethod
    def default(cls):
        return cls.query.filter_by(is_default=True)[0]
