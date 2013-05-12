# -*- coding: utf-8 -*-
from datetime import datetime

from .utils import random_string
from .extensions import db



user_question_relation = db.Table('user_question_relation',
  db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
  db.Column('question_id', db.Integer, db.ForeignKey('questions.id')),
  db.Column('scheduled_for', db.DateTime(timezone=True)),
  db.Column('notification_method', db.String(255))
)


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

