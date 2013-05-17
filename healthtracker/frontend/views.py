# -*- coding: utf-8 -*-
from flask import (Blueprint, render_template, current_app, request,
                   flash, url_for, redirect, session, abort, current_app, 
                   json)

from ..users.forms import LoginForm
from ..utils import format_date, is_valid_email



frontend = Blueprint('frontend', __name__, template_folder='templates')


@frontend.route('/')
def landing():
    return render_template("landing.html", login_form=LoginForm())

@frontend.route('/learn-more', methods=['POST', 'GET'])
def learn_more():
    if request.method == "POST":
        email = request.form.get("email")
        send_simple_email("Request For Info",
                          "{} has requested information on HealthTracker".format(email),
                          "isaachodes@gmail.com")
        return redirect(url_for("learn_more"))
    else: 
        return render_template("learn_more.html")

@frontend.route("/ptportal")
def ptportal():
    return render_template("patient_portal.html")

@frontend.route("/drconsole")
def drconsole():
    return render_template("doctor_console.html")

@frontend.route("/privacy-policy")
def privacy():
    return render_template("privacy.html")

@frontend.route("/about-us")
def about():
    return render_template("about.html")

@frontend.route("/contact-us")
def contact():
    return render_template("contact_us.html")

@frontend.route("/terms-of-service")
def tos():
    return render_template("tos.html")

@frontend.route("/messages")
def messages():
    return render_template("messages.html")
