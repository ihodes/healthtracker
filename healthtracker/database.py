# -*- coding: utf-8 -*-
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, \
     Boolean, ForeignKey, Sequence
from sqlalchemy.orm import scoped_session, sessionmaker, backref, relation, \
     relationship
from sqlalchemy.ext.declarative import declarative_base

from healthtracker import app
from healthtracker.utils import random_string


engine = create_engine(app.config['DATABASE_URI'],
                       convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))

def init_db():
    Model.metadata.create_all(bind=engine)

Model = declarative_base(name='Model')
Model.query = db_session.query_property()


class User(Model):
    __tablename__ = "users"
    id = Column(Integer, Sequence('users_id_seq'), primary_key=True)
    email = Column(String(255), unique=True)
    auth_token = Column(String, unique=True)
    statuses = relationship("Status", backref="users", lazy="dynamic")
    is_confirmed = Column(Boolean, default=False)
    is_approved = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)

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

    def approve(self):
        self.is_approved = True
        self.save()

    def unapprove(self):
        self.is_approved = False
        self.save()

    def add_status(self, value):
        status = Status(self, value)
        db_session.add(status)
        db_session.commit()

    def save(self):
        db_session.add(self)
        db_session.commit()

    def delete(self):
        db_session.delete(self)
        db_session.commit()

    @staticmethod
    def create(email):
        if User.query.filter_by(email=email).first() is None:
            user = User(email)
            db_session.add(user)
            db_session.commit()
            return user
        return None


class Status(Model):
    __tablename__ = "statuses"
    id = Column(Integer, Sequence('statuses_id_seq'), primary_key=True)
    value = Column(Integer)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True),
                        default=datetime.utcnow)
    
    def __init__(self, user, value):
        self.user_id = user.id
        self.value = value

    def __repr__(self):
        return "<Status('%s' :: '%r')>" % (self.user.email, self.value)

