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
    if user is None:
        flash(u"""invalid authentication""", "error")
        return redirect(url_for("frontend.messages"))

    questions = []
    for question in user.questions:
        answers = [{'date':a.created_at.strftime("%d-%m-%Y %H:%M"), 'value':a.value}
                   for a in user.answers.filter_by(question=question).order_by('created_at ASC')]
        questions.append({'name': question.name,
                          'text': question.text,
                          'answers': json.dumps({'answers':answers}),
                          'qmax': question.max_value,
                          'qmin': question.min_value
                          })
    return render_template('tracker.html', questions=questions, user=user)


@tracker.route("/track/<question_id>/")
@provide_user_from_auth
def track(user, question_id=None):
    question = Question.query.get(question_id)
    if user is None:
        flash(u"""You can't update your status; use the newest email from us,
              or sign up for an account if you don't have one.""", 'error')
        return redirect(url_for("frontend.messages"))
    value = request.args.get("value", None)
    user.answers.append(Answer(user, question, value))
    user.save()
    flash(u"""You've reported a {} out of {} for question '{}'""".format(value, question.max_value, question.name), 'info')
    return redirect(url_for('.show', auth_token=user.auth_token))

