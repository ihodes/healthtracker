# -*- coding: utf-8 -*-
from ..extensions import db
from ..database import Status
from ..utils import random_string


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, db.Sequence('users_id_seq'), primary_key=True)
    email = db.Column(db.String(255), unique=True)
    auth_token = db.Column(db.String, unique=True)
    statuses = db.relationship("Status", backref="user", lazy="dynamic")
    is_confirmed = db.Column(db.Boolean, default=False)
    is_approved = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)

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

    def add_status(self, value):
        status = Status(self, value)
        db.session.add(status)
        db.session.commit()

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

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
