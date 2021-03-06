# -*- coding: utf-8 -*-
from datetime import datetime

from .utils import random_string
from .extensions import db
from sqlalchemy.ext.associationproxy import association_proxy
from flask.ext.bcrypt import check_password_hash
from flask.ext.login import UserMixin


class ScheduledQuestion(db.Model):
    __tablename__ = 'scheduled_questions'
    id = db.Column(db.Integer, db.Sequence('scheduled_questions_id_seq'), primary_key=True)
    user_id = db.Column('user_id', db.Integer, db.ForeignKey('users.id'))
    question_id = db.Column('question_id', db.Integer, db.ForeignKey('questions.id'))
    scheduled_for = db.Column('scheduled_for', db.DateTime())
    notification_method = db.Column('notification_method', db.String(255))

    question = db.relationship('Question', backref=db.backref('scheduling_user_assocs', lazy='dynamic'))
    user = db.relationship('User', backref='scheduled_question_assocs')

    def __repr__(self):
        return "<ScheduledQuestion({}::{}::{})>".format(self.user.name, self.question.name, self.notification_method)


class Answer(db.Model):
    __tablename__ = "answers"
    id = db.Column(db.Integer, db.Sequence('answers_id_seq'), primary_key=True)
    value = db.Column(db.Text)
    state = db.Column(db.String(255), default="pending")
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    question_id = db.Column(db.Integer, db.ForeignKey("questions.id"))
    question = db.relationship("Question", backref=db.backref('answers', lazy='dynamic'))
    asked_at = db.Column(db.DateTime, default=datetime.utcnow)
    answered_at = db.Column(db.DateTime)

    def __init__(self, user, question):
        self.user_id = user.id
        self.question_id = question.id

    def __repr__(self):
        return "<Answer({}::{}::{}:{})>".format(self.user.email,
                                             self.value,
                                             self.question.name,
                                             self.question.id)

    def answer(self, value):
        answer.value = value
        answer.state = 'answered'
        answer.answered_at = datetime.datetime.now()

    @classmethod
    def pend(klass, user, question):
        current = user.answers.filter_by(state='pending', question=question).all()
        if len(current) > 0:
            for answer in current:
                answer.state = 'unanswered'
                db.session.add(answer)
        answer = klass(user, question)
        db.session.add(answer)
        db.session.commit()



class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, db.Sequence('users_id_seq'), primary_key=True)
    email = db.Column(db.String(255), unique=True)
    encrypted_password = db.Column(db.String(60))
    auth_token = db.Column(db.String, unique=True)
    answers = db.relationship("Answer", backref="user", lazy="dynamic")

    is_confirmed = db.Column(db.Boolean, default=False)
    is_approved = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)

    name = db.Column(db.Text)
    notes = db.Column(db.Text)
    timezone = db.Column(db.String(60))

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

    # For Flask-Login
    def get_auth_token(self):
        return self.id # TK TODO needs to be more secure than this... c.f. https://flask-login.readthedocs.org/en/latest/

    def check_password(self, candidate):
        return check_password_hash(self.encrypted_password, candidate)

    # hack for now
    def wq(self):
        return sum(map(lambda a: float(a.value), self.answers.filter_by(question_id=Question.default().id, state='answered').order_by('answered_at ASC').all()[-7:]))/7
    # hack for now
    def last_30_days_str(self):
        return str(map(lambda a: int(a.value), self.answers.filter_by(question_id=Question.default().id, state='answered').order_by('answered_at ASC').all()[-30:]))[1:-1]

    def last_asked_questions(self, method='text'):
        """Looks in redis to see the last questions asked by a given method,
        sorted by age."""
        return []

    @staticmethod
    def create(email):
        if User.query.filter_by(email=email).first() is None:
            user = User(email)
            user.save()
            return user
        return None

    @staticmethod
    def find_by(**kwargs):
        return User.query.filter_by(**kwargs).first()


class Question(db.Model):
    __tablename__ = "questions"
    id = db.Column(db.Integer, db.Sequence('questions_id_seq'), primary_key=True)
    name = db.Column(db.String(255))
    qtype = db.Column(db.String(255))
    text = db.Column(db.Text)

    is_default = db.Column(db.Boolean, default=False)
    is_public = db.Column(db.Boolean, default=False)

    min_value = db.Column(db.Integer)
    max_value = db.Column(db.Integer)

    created_by = db.Column(db.Integer, db.ForeignKey("users.id"))

    def __init__(self, name=None, text=None, min_value=0, max_value=5):
        self.name = name
        self.text = text
        # well, this is hacky. TK fix with WTForms?
        self.min_value = 0 if min_value == '' else int(min_value)
        self.max_value = 5 if max_value == '' else int(max_value)

    def __repr__(self):
        return "<Question({})::{}>".format(self.id, self.name)

    @classmethod
    def default(cls):
        return cls.query.filter_by(is_default=True)[0]

    def validate(self, answer):
        """TK TODO
        Return whether or not the answer is valid (based on question's qtype)
        """
        return True
