# -*- coding: utf-8 -*-
from datetime import datetime

from .utils import random_string
from .extensions import db



user_question_relation = db.Table('user_question_relation',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('question_id', db.Integer, db.ForeignKey('questions.id'))
)


class Status(db.Model):
    __tablename__ = "statuses"
    id = db.Column(db.Integer, db.Sequence('statuses_id_seq'), primary_key=True)
    value = db.Column(db.Integer)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
#    question_id = db.Column(db.Integer, db.ForeignKey("questions.id"))

    created_at = db.Column(db.DateTime(timezone=True),
                           default=datetime.utcnow)

#    question = db.relationship("Question", backref=db.backref('statuses', lazy='dynamic')) # TK TODO: implement

    
    def __init__(self, user, value):
        self.user_id = user.id
        self.value = value

    def __repr__(self):
        return "<Status('%s' :: '%r')>" % (self.user.email, self.value)

