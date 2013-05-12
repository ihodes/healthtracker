# -*- coding: utf-8 -*-
from ..extensions import db
from ..database import user_question_relation



class Question(db.Model):
    __tablename__ = "questions"
    id = db.Column(db.Integer, db.Sequence('questions_id_seq'), primary_key=True)
    name = db.Column(db.String(255), unique=True)
    text = db.Column(db.Text)

    def __init__(self, name, text):
        self.name = name
        self.text = text

    def __repr__(self):
        return "<Question::{}>".format(self.name)
