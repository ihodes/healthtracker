# -*- coding: utf-8 -*-
from flask import (Blueprint, json, url_for, redirect, render_template, flash, request)

from ..extensions import db
from ..view_helpers import provide_user_from_auth



tracker = Blueprint('tracker', __name__,
                    url_prefix='/tracker',
                    static_folder='static',
                    template_folder='templates')


@tracker.route("/")
@provide_user_from_auth
def show(user):
    if user is None:
        flash(u"""invalid authentication""", "error")
        return redirect(url_for("frontend.messages"))

    statuses = [{'date':s.created_at.strftime("%d-%m-%Y"), 'value':s.value}
                for s in user.statuses.all()]
    return render_template("tracker.html", statuses=json.dumps({'statuses':statuses}))


@tracker.route("/track")
@provide_user_from_auth
def track(user):
    if user is None:
        flash(u"""You can't update your status; use the newest email from us,
              or sign up for an account if you don't have one.""", "error")
        return redirect(url_for("frontend.messages"))

    value = request.args.get("value", None)
    user.add_status(value)
    user.reset_auth_token() # to prevent accidental multiple updates
    flash(u"""You've reported a {} out of 5.""".format(value), "info")
    return redirect(url_for('.show', auth_token=user.auth_token))

