# -*- coding: utf-8 -*-
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager



db = SQLAlchemy()

lm = LoginManager()
lm.login_view = 'user.login'
