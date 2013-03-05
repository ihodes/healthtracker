# -*- coding: utf-8 -*-
from flask import render_template, session, redirect, url_for, request, \
     flash, g, jsonify, abort
from healthtracker.database import db_session, User
from healthtracker.utils import format_date
from healthtracker.mailer import send_admin_login
from healthtracker import app


@app.route("/")
def index():
    return render_template("landing.html")


@app.route("/subscribe", methods=["POST"])
def subscribe():
    email = request.form.get("email")
    if "@" in email: # assume this is enough, for now
        User.create_user(email)
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
