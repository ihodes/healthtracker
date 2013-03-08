# -*- coding: utf-8 -*-
from flask import render_template, session, redirect, url_for, request, \
     flash, g, jsonify, abort

from healthtracker.database import User
from healthtracker.utils import format_date, is_valid_email
from healthtracker.view_helpers import get_user_by_auth, get_user_by_id, \
     admin_required
from healthtracker.mailer import send_admin_login, send_status_update_email, \
     send_approval_email, send_confirmation_email
from healthtracker import app


@app.route("/")
def index():
    return render_template("landing.html")


@app.route("/subscribe", methods=["POST"])
def subscribe():
    email = request.form.get("email")
    if is_valid_email(email):
        user = User.create(email)
        if user:
            send_confirmation_email(user)
            flash(u"""You've been subscribed. An email has been sent
                  to {0} with more information""".format(email), "info")
    else:
        flash(u""""{0}" is not a valid email address:
              please re-enter your email.""".format(email), "error")
    return redirect(url_for("index"))


@app.route("/confirm-email")
def confirm_email():
    user = get_user_by_auth(request)

    if user is not None:
        user.confirm()
        flash(u"""We've confirmed your email address; you can expect an email
                  from us after you've been approved.""", "info")
    return redirect(url_for("index"))
    

@app.route("/tracker")
def tracker():
    value = request.args.get('value', None)
    user = get_user_by_auth(request)

    if user is None:
        flash(u"""You can't update your status; use the newest email from us,
              or sign up for an account if you don't have one.""", "error")
        return redirect(url_for("index"))

    if value is not None:
        user.add_status(value)
        user.reset_auth_token() # to prevent accidental multiple updates
        flash(u"""You've reported a {} out of 5.""".format(value), "info")

    statuses = []
    for status in user.statuses.order_by("created_at desc").all():
        statuses.append((status.value, format_date(status.created_at)))

    return render_template("tracker.html", statuses=statuses)


@app.route("/admin")
def admin():
    admin = get_user_by_auth(request)
    if admin is None or not admin.is_admin:
        send_admin_login()
        return "Must be administrator. (Email sent to admin)."

    users = User.query.all()
    return render_template("admin.html", users=users, auth_token=admin.auth_token)


@app.route("/toggle_approve_user", methods=["POST"])
@admin_required
def toggle_approve_user(admin):
    user = get_user_by_id(request)
    if user.is_approved:
        user.unapprove()
    else:
        if not user.is_confirmed:
            user.confirm()
        user.approve()
        send_approval_email(user)
    return redirect(url_for("admin", auth_token=admin.auth_token))

@app.route("/delete_user", methods=["POST"])
@admin_required
def delete_user(admin):
    user = get_user_by_id(request)
    if user:
        user.delete()
    return redirect(url_for("admin", auth_token=admin.auth_token))


@app.route("/reset_auth_user", methods=["POST"])
@admin_required
def reset_auth_user(admin):
    user = get_user_by_id(request)
    user.reset_auth_token()
    return redirect(url_for("admin", auth_token=admin.auth_token))


@app.route("/send_update_email_user", methods=["POST"])
@admin_required
def send_update_email_user(admin):
    user = get_user_by_id(request)
    send_status_update_email(user)
    return redirect(url_for("admin", auth_token=admin.auth_token))
