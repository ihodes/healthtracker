# -*- coding: utf-8 -*-
from flask import Flask, session, render_template

app = Flask(__name__)
app.config.from_object('config')


@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


@app.teardown_request
def remove_db_session(exception):
    db_session.remove()


from healthtracker.views import *
from healthtracker.database import User, db_session
from healthtracker import utils
