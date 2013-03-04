# -*- coding: utf-8 -*-

import string, random, datetime, requests, os

# for email template rendering... 
# from jinja2 import Environment, PackageLoader
# env = Environment(loader=PackageLoader('app', 'templates/emails'))

from flask import (Flask, request, session, g, redirect, url_for, abort,
                   render_template, flash, abort)
from flask.ext.sqlalchemy import SQLAlchemy


# Application Settings
SECRET_KEY = ':\x90[\xf2F[X\xcbA\xcbA\xcf\xd7U3\xdb+/b\xf0\x1f\xe9\x00\xe4'
DEBUG = True
SQL_DB_URI = 'sqlite:///dev.db'

app = Flask(__name__)
# app.config.from_object('yourapplication.default_settings') => object with config
# app.config.from_envvar('YOURAPPLICATION_SETTINGS') => /path/to/config/config.py
app.config['SQLALCHEMY_DATABASE_URI'] = SQL_DB_URI
app.secret_key = SECRET_KEY
app.debug = DEBUG

db = SQLAlchemy(app)
HOST = os.environ.get("HOST_NAME", "healthtracker.herokuapp.com")


## Models
class User(db.Model):
    id = db.Column(db.Integer, db.Sequence('user_id_seq'), primary_key=True)
    email = db.Column(db.String(255), unique=True)
    auth_token = db.Column(db.String, unique=True)
    statuses = db.relationship("Status", backref="user", lazy="dynamic")
    is_approved = db.Column(db.Boolean)
    is_admin = db.Column(db.Boolean, default=False)

    def __init__(self, email, is_approved=False):
        self.email = email
        self.auth_token = random_string(36)
        self.is_approved = is_approved

    def __repr__(self):
        return "<User('%s')>" % (self.email)

    def reset_auth_token(self):
        self.auth_token = random_string(36)
        db.session.add(self)
        db.session.commit()

    def add_status(self, value):
        status = Status(self, value)
        self.reset_auth_token()
        db.session.add(status)
        db.session.commit()


class Status(db.Model):
    id = db.Column(db.Integer, db.Sequence('status_id_seq'), primary_key=True)
    value = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    created_at = db.Column(db.DateTime(timezone=True),
                           default=datetime.datetime.utcnow)
    
    def __init__(self, user, value):
        self.user_id = user.id
        self.value = value

    def __repr__(self):
        return "<Status('%s' :: '%r')>" % (self.user.email, self.value)



### Helpers
def create_user(email):
    db.session.add(User(email))
    db.session.commit()

def random_string(size=32):
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for __ in range(size))

def format_date(datetime):
    year = datetime.year
    month = datetime.month
    day = datetime.day
    return "{0}/{1}, {2}".format(day, month, year)


## Views
@app.route("/")
def index():
    return render_template("landing.html")


@app.route("/subscribe", methods=["POST"])
def subscribe():
    email = request.form.get("email")
    if "@" in email: # assume this is enough, for now
        create_user(email)
        flash(u"""You've been subscribed. An email has been sent
              to {0} with more information""".format(email))
    else:
        flash(u""""{0}" is not a valid email address:
              please re-enter your email.""".format(email), "error")
    return redirect(url_for("index"))


@app.route("/unsubscribe", methods=["GET", "POST"])
def unsubscribe():
    if request.method == "GET":
        return "unsubscribe form"
    elif request.method == "POST":
        flash("You've been unsubscribed. We're sorry to see you go! You can always subscribe again below to recieve emails for us.", "info")
        return redirect(url_for("index"))


@app.route("/tracker") # pull out url params here; this is how we track everything
def tracker():
    auth_token = request.args.get('auth_token', None)
    value = int(request.args.get('value', -100))
    user = User.query.filter_by(auth_token=auth_token).first_or_404()
    if auth_token is None or value is None or user is None or value < 0 or value > 5:
        return abort(404)

    user.add_status(value)
    user.reset_auth_token()
    statuses = []
    for status in user.statuses.all():
        statuses.append((status.value, format_date(status.created_at)))

    return render_template("tracker.html", value=value, total_statuses=len(statuses), statuses=statuses)


# this and the below method need to be secured
@app.route("/admin")
def admin():
    auth_token = request.args.get('auth_token', None)
    user = User.query.filter_by(auth_token=auth_token).first()
    if user is None or not user.is_admin:
        send_admin_login()
        return abort(401)
    else:
        users = []
        for user in User.query.all():
            users.append(user)
        return render_template("admin.html", users=users)


@app.route("/approve", methods=["POST"])
def approve():
    user_id = request.form.get("user_id", None)
    if user_id is not None:
        user = User.query.get(user_id)
    user.is_approved = True
    db.session.add(user)
    db.session.commit()
    return redirect(url_for("admin"))



def send_admin_login():
    api_endpoint = "https://api.mailgun.net/v2/healthtracker.mailgun.org/messages"
    api_key = "key-25pn6z0fogz-783zc7gcloa8gs23qkq2"
    from_email = "Health Tracker <hello@healthtracker.mailgun.org>"
    email_subject = "HealthTracker admin"

    user = User.query.filter_by(email="isaachodes@gmail.com").first()

    email_text = "click to login: http://{0}/admin?auth_token={1}".format(HOST, user.auth_token)

    return requests.post(api_endpoint,
                         auth=("api", api_key),
                         data={"from": from_email,
                               "to": "isaachodes@gmail.com",
                               "subject": email_subject,
                               "text": email_text})



if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
