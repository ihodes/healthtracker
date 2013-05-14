# -*- coding: utf-8 -*-
from flask import (Blueprint, json, url_for, redirect, render_template, flash, request,
                   current_app)

from ..extensions import db
from ..view_helpers import provide_user_from_auth
from ..database import Answer, Question



tracker = Blueprint('tracker', __name__,
                    url_prefix='/tracker',
                    static_folder='static',
                    template_folder='templates')


@tracker.route("/")
@provide_user_from_auth
def show(user):
    # TODO TK: haxxx just to get it working for the regular WQ question
    question = Question.query.get(1)

    if user is None:
        flash(u"""invalid authentication""", "error")
        return redirect(url_for("frontend.messages"))

    answers = [{'date':a.created_at.strftime("%d-%m-%Y"), 'value':a.value}
                for a in user.answers.filter_by(question=question).order_by('created_at ASC')]
    return render_template('tracker.html', answers=json.dumps({'answers':answers}))


@tracker.route("/track")
@provide_user_from_auth
def track(user):
    # TODO TK: haxxx just to get it working for the regular WQ question
    question = Question.query.get(1)

    if user is None:
        flash(u"""You can't update your status; use the newest email from us,
              or sign up for an account if you don't have one.""", 'error')
        return redirect(url_for("frontend.messages"))

    value = request.args.get("value", None)
    user.answers.append(Answer(user, question, value))
    user.reset_auth_token() # to prevent accidental multiple updates (as this is a GET)
    # user.save() -- TK not needed because reset_auth_token commits the user, but would be needed otherwise
    flash(u"""You've reported a {} out of 5.""".format(value), 'info')
    return redirect(url_for('.show', auth_token=user.auth_token))

