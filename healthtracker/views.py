# -*- coding: utf-8 -*-
from flask import render_template, session, redirect, url_for, request, \
     flash, g, jsonify, abort

from healthtracker.db import Patient, Provider, Organization, db
from healthtracker.utils import format_date, is_valid_email
from healthtracker.view_helpers import get_patient_by_auth, get_patient_by_id, \
     require_admin, provide_patient_from_auth, provide_patient_from_id
from healthtracker.mailer import send_admin_login, send_status_update_email, \
     send_approval_email, send_confirmation_email, send_login_email, \
     send_simple_email
from healthtracker import app



@app.route("/")
def index():
    return render_template("landing.html")

@app.route("/admin/manager")
def admin_manager():
    # should have auth here (for me & jinai etc)
    # stopgap measure could be hardcoded pw for demo purposes
    return render_template("admin/manager.html", organizations=Organization.query.all())


@app.route("/organizations", methods=["POST"])
def organizations():
    organization = Organization(name=request.form.get("name"))
    db.session.add(organization)
    db.session.commit()
    return redirect(url_for("admin_manager"))


@app.route("/organizations/<id>/edit")
def organizations_edit(id):
    organization = Organization.query.filter_by(id=id).first_or_404()
    return render_template("organizations/edit.html", organization=organization)


@app.route("/providers", methods=["POST"])
def provider():
    provider = Provider(name=request.form.get("name"), username=request.form.get("username"),
                        email=request.form.get("email"), password=request.form.get("password"), 
                        organization_id=request.form.get("organization_id"))
    db.session.add(provider)
    db.session.commit()
    return redirect(url_for("organizations_edit", id=request.form.get("organization_id")))


@app.route("/register", methods=["POST", "GET"])
def register():
    return render_template("register.html")


@app.route("/login", methods=["POST"])
def login():
    return redirect(url_for("patient_portal"))


@app.route("/portal")
def patient_portal():
    return render_template("patient_portal.html")


@app.route("/dr-console")
def doctor_console():
    return render_template("doctor_console.html")


@app.route("/learn-more", methods=["POST", "GET"])
def learn_more():
    if request.method == "POST":
        email = request.form.get("email")
        send_simple_email("Request For Info",
                          "{} has requested information on HealthTracker".format(email),
                          "isaachodes@gmail.com")
        return redirect(url_for("learn_more"))
    else: 
        return render_template("learn_more.html")


@app.route("/us/privacy")
def privacy():
    return render_template("privacy.html")


@app.route("/us/about")
def about():
    return render_template("about.html")


@app.route("/us/contact")
def contact():
    return render_template("contact_us.html")


@app.route("/messages")
def messages():
    return render_template("messages.html")


@app.route("/subscribe", methods=["POST"])
def subscribe():
    email = request.form.get("email")
    if is_valid_email(email):
        patient = Patient.find_by(email=email)
        if patient is None:
            patient = Patient.create(email)
            send_confirmation_email(patient)
            flash(u"""You've been subscribed. An email has been sent
                  to {0} with more information""".format(email), "info")
        elif not patient.is_confirmed:
            flash(u"""Check your email to confirm your subscription (check your spam if you don't see it within a minute!)""", "info")
            send_confirmation_email(patient)
        else:
            send_login_email(patient)
            flash(u"""We've sent you a link to log in with: check your email.""".format(email), "info")
    else:
        flash(u""""{0}" is not a valid email address:
              please re-enter your email.""".format(email), "error")
        return redirect(url_for("index"))
    return redirect(url_for("messages"))


@app.route("/confirm-email")
@provide_patient_from_auth
def confirm_email(patient):
    if patient is not None:
        patient.confirm()
        flash(u"""We've confirmed your email address; you can expect an email
                  from us after you've been approved.""", "info")
    return redirect(url_for("messages"))
    

@app.route("/tracker")
@provide_patient_from_auth
def tracker(patient):
    value = request.args.get("value", None)
    if patient is None:
        flash(u"""You can't update your status; use the newest email from us,
              or sign up for an account if you don't have one.""", "error")
        return redirect(url_for("messages"))
    if value is not None:
        patient.add_status(value)
        patient.reset_auth_token() # to prevent accidental multiple updates
        flash(u"""You've reported a {} out of 5.""".format(value), "info")

    statuses = [status.value for status in patient.statuses.all()]
    return render_template("tracker.html", statuses=statuses)


@app.route("/unsubscribe")
@provide_patient_from_auth
def unsubscribe(patient):
    if patient is None:
        flash(u"""Use the unsubscribe link from your newest email to unsubscribe (this link has expired!)""", "error")
    else:
        patient.unconfirm()
        flash(u"""You've been unsubscribed: we're sorry to see you go.""", "info")
    return redirect(url_for("messages"))


@app.route("/admin")
@provide_patient_from_auth
def admin(admin):
    if admin is None or not admin.is_admin:
        send_admin_login()
        return "Must be administrator. (Email sent to admin)."
    patients = Patient.query.all()
    return render_template("admin.html", patients=patients, auth_token=admin.auth_token)


@app.route("/toggle_approve_patient", methods=["POST"])
@require_admin
@provide_patient_from_id
def toggle_approve_patient(patient, admin):
    if patient.is_approved:
        patient.unapprove()
    else:
        if not patient.is_confirmed:
            patient.confirm()
        patient.approve()
        send_approval_email(patient)
    return redirect(url_for("admin", auth_token=admin.auth_token))


@app.route("/delete_patient", methods=["POST"])
@require_admin
@provide_patient_from_id
def delete_patient(patient, admin):
    patient.delete()
    return redirect(url_for("admin", auth_token=admin.auth_token))


@app.route("/reset_auth_patient", methods=["POST"])
@require_admin
@provide_patient_from_id
def reset_auth_patient(patient, admin):
    patient.reset_auth_token()
    return redirect(url_for("admin", auth_token=admin.auth_token))


@app.route("/send_update_email_patient", methods=["POST"])
@require_admin
@provide_patient_from_id
def send_update_email_patient(patient, admin):
    send_status_update_email(patient)
    return redirect(url_for("admin", auth_token=admin.auth_token))
