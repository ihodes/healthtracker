# -*- coding: utf-8 -*-
from ..extensions import db
from ..database import user_question_relation


class Question(db.Model):
    __tablename__ = "questions"
    id = db.Column(db.Integer, db.Sequence('questions_id_seq'), primary_key=True)
    name = db.Column(db.String(255), unique=True)
    text = db.Column(db.Text)
    min_value = db.Column(db.Integer)
    max_value = db.Column(db.Integer)

    def __init__(self, name, text, min_value=0, max_value=10):
        self.name = name
        self.text = text
        self.min_value = min_value
        self.max_value = max_value

