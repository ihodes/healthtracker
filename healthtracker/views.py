# -*- coding: utf-8 -*-
from flask import render_template, session, redirect, url_for, request, \
     flash, g, jsonify, abort
from healthtracker.database import db_session, User
from healthtracker.utils import format_date, is_valid_email
from healthtracker.mailer import send_admin_login, send_status_update_email
from healthtracker import app


@app.route("/")
def index():
    return render_template("landing.html")


@app.route("/subscribe", methods=["POST"])
def subscribe():
    email = request.form.get("email")
    if is_valid_email(email):
        if User.create_user(email):
            flash(u"""You've been subscribed. An email has been sent
                  to {0} with more information""".format(email), "info")
    else:
        flash(u""""{0}" is not a valid email address:
              please re-enter your email.""".format(email), "error")
    return redirect(url_for("index"))


@app.route("/tracker") # pull out url params here; this is how we track everything
def tracker():
    auth_token = request.args.get('auth_token', None)
    value = int(request.args.get('value', None))
    user = User.query.filter_by(auth_token=auth_token).first()

    if auth_token is None or value is None or user is None or 0 > value > 5:
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
        return render_template("admin.html", users=users, auth_token=auth_token)


@app.route("/approve_user", methods=["POST"])
def approve_user():
    auth_token = request.form.get('auth_token', None)
    user = User.query.filter_by(auth_token=auth_token).first()
    if user is None or not user.is_admin:
        return abort(401)

    user_id = request.form.get("user_id", None)
    if user_id is not None:
        user = User.query.get(user_id)
    user.is_approved = True
    db_session.add(user)
    db_session.commit()
    return redirect(url_for("admin", auth_token=auth_token))

@app.route("/delete_user", methods=["POST"])
def delete_user():
    auth_token = request.form.get('auth_token', None)
    user = User.query.filter_by(auth_token=auth_token).first()
    if user is None or not user.is_admin:
        return abort(401)


    user_id = request.form.get("user_id", None)
    if user_id is not None:
        user = User.query.get(user_id)
    db_session.delete(user)
    db_session.commit()
    return redirect(url_for("admin", auth_token=auth_token))

@app.route("/reset_auth_user", methods=["POST"])
def approve_user():
    auth_token = request.form.get('auth_token', None)
    user = User.query.filter_by(auth_token=auth_token).first()
    if user is None or not user.is_admin:
        return abort(401)

    user_id = request.form.get("user_id", None)
    if user_id is not None:
        user = User.query.get(user_id)
    user.reset_auth_token()

    return redirect(url_for("admin", auth_token=auth_token))

@app.route("/send_update_email_user", methods=["POST"])
def send_update_email_user():
    auth_token = request.form.get('auth_token', None)
    user = User.query.filter_by(auth_token=auth_token).first()
    if user is None or not user.is_admin:
        return abort(401)

    user_id = request.form.get("user_id", None)
    if user_id is not None:
        user = User.query.get(user_id)
    send_status_update_email(user)

    return redirect(url_for("admin", auth_token=auth_token))
