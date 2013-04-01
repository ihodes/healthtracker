# -*- coding: utf-8 -*-
from flask import render_template, session, redirect, url_for, request, \
     flash, g, jsonify, abort

from healthtracker.database import User
from healthtracker.utils import format_date, is_valid_email
from healthtracker.view_helpers import get_user_by_auth, get_user_by_id, \
     require_admin, provide_user_from_auth, provide_user_from_id
from healthtracker.mailer import send_admin_login, send_status_update_email, \
     send_approval_email, send_confirmation_email, send_login_email
from healthtracker import app


@app.route("/")
def index():
    return render_template("landing.html")


@app.route("/learn-more")
def learn_more():
    return render_template("learn_more.html")


@app.route("/drconsole")
def drconsole():
    return render_template("doctor_console.html")


@app.route("/ptportal")
def ptportal():
    return render_template("patient_portal.html")


@app.route("/messages")
def messages():
    return render_template("messages.html")


@app.route("/subscribe", methods=["POST"])
def subscribe():
    email = request.form.get("email")
    if is_valid_email(email):
        user = User.find_by(email=email)
        if user is None:
            user = User.create(email)
            send_confirmation_email(user)
            flash(u"""You've been subscribed. An email has been sent
                  to {0} with more information""".format(email), "info")
        elif not user.is_confirmed:
            flash(u"""Check your email to confirm your subscription (check your spam if you don't see it within a minute!)""", "info")
            send_confirmation_email(user)
        else:
            send_login_email(user)
            flash(u"""We've sent you a link to log in with: check your email.""".format(email), "info")
    else:
        flash(u""""{0}" is not a valid email address:
              please re-enter your email.""".format(email), "error")
        return redirect(url_for("index"))
    return redirect(url_for("messages"))


@app.route("/confirm-email")
@provide_user_from_auth
def confirm_email(user):
    if user is not None:
        user.confirm()
        flash(u"""We've confirmed your email address; you can expect an email
                  from us after you've been approved.""", "info")
    return redirect(url_for("messages"))
    

@app.route("/tracker")
@provide_user_from_auth
def tracker(user):
    value = request.args.get("value", None)
    if user is None:
        flash(u"""You can't update your status; use the newest email from us,
              or sign up for an account if you don't have one.""", "error")
        return redirect(url_for("messages"))
    if value is not None:
        user.add_status(value)
        user.reset_auth_token() # to prevent accidental multiple updates
        flash(u"""You've reported a {} out of 5.""".format(value), "info")

    statuses = [status.value for status in user.statuses.all()]
    return render_template("tracker.html", statuses=statuses)


@app.route("/unsubscribe")
@provide_user_from_auth
def unsubscribe(user):
    if user is None:
        flash(u"""Use the unsubscribe link from your newest email to unsubscribe (this link has expired!)""", "error")
    else:
        user.unconfirm()
        flash(u"""You've been unsubscribed: we're sorry to see you go.""", "info")
    return redirect(url_for("messages"))


@app.route("/admin")
@provide_user_from_auth
def admin(admin):
    if admin is None or not admin.is_admin:
        send_admin_login()
        return "Must be administrator. (Email sent to admin)."
    users = User.query.all()
    return render_template("admin.html", users=users, auth_token=admin.auth_token)


@app.route("/toggle_approve_user", methods=["POST"])
@require_admin
@provide_user_from_id
def toggle_approve_user(user, admin):
    if user.is_approved:
        user.unapprove()
    else:
        if not user.is_confirmed:
            user.confirm()
        user.approve()
        send_approval_email(user)
    return redirect(url_for("admin", auth_token=admin.auth_token))


@app.route("/delete_user", methods=["POST"])
@require_admin
@provide_user_from_id
def delete_user(user, admin):
    user.delete()
    return redirect(url_for("admin", auth_token=admin.auth_token))


@app.route("/reset_auth_user", methods=["POST"])
@require_admin
@provide_user_from_id
def reset_auth_user(user, admin):
    user.reset_auth_token()
    return redirect(url_for("admin", auth_token=admin.auth_token))


@app.route("/send_update_email_user", methods=["POST"])
@require_admin
@provide_user_from_id
def send_update_email_user(user, admin):
    send_status_update_email(user)
    return redirect(url_for("admin", auth_token=admin.auth_token))
