# -*- coding: utf-8 -*-
from flask import (Blueprint, json, url_for, redirect, render_template, flash, request,
                   current_app, abort)
from flask.ext.login import login_user

from ..extensions import db
from ..view_helpers import provide_user_from_auth
from ..database import Answer, Question
from ..sms import send_text

import datetime
import re


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
        ans = user.answers.filter_by(question=question,
                                     state='answered').order_by('answered_at ASC').all()
        answers = [{'date':a.answered_at.strftime("%d-%m-%Y %H:%M"), 'value':a.value}
                   for a in ans]
        # TK hacky multi dispatch
        if question.qtype == 'multi_numeric':
            qmax = question.max_value
            qmin = question.min_value
        elif question.qtype == 'yesno':
            qmax = 1
            qmin = 0
        elif question.qtype == 'numeric':
            qmax = max(int(a.value) for a in ans) if len(ans) else 0
            qmin = min(int(a.value) for a in ans) if len(ans) else 0

        questions.append({'name'   : question.name,
                          'text'   : question.text,
                          'answers': json.dumps({'answers':answers}),
                          'qmax'   : qmax,
                          'qmin'   : qmin})
    return render_template('tracker.html', questions=questions, user=user)


@tracker.route('/track')
def text_track():
    """This is used to gather answers from Twilio."""
    phone_number = request.get('From')
    body = request.get('Body')
    if not phone_number: abort(404)
    # we're assuming no spoofing of numbers here...
    user = User.query.filter_by(phone_number=phone_number).first_or_404()
    last_asked_questions = user.last_asked_questions() # get from Redis (sorted) TK TODO
    # ^ e.g. if at 1pm we sent 2 questions, and they were not answered, then at 5pm 
    #        we sent 2 questions, any answers will be just for the most recent Qs.
    splitter = re.compile(',|,?\s+')
    values = [val for val in splitter.split(body) if val]

    # need to ensure same # of answers to prevent errors
    if len(values) != len(last_asked_questions): return 

    for question, value in zip(last_asked_questions, values):
        if question.validate(value): # TK to implement
            answer = Answer.query.filter_by(state='pending',
                                            question_id=question.id,
                                            user_id=user.id).first()
            answer.answer(value)
            db.session.add(answer)
        else:
            return # some error; ask for qs again

    send_text("Thanks for recording your answers! Stay well!") # or something


@tracker.route('/track/<question_id>/')
@provide_user_from_auth
def online_track(user, question_id=None):
    question = Question.query.get_or_404(question_id)
    if user is None:
        flash(u"""You can't update your status; use the newest email from us (this one has expired)
              or sign up for an account if you don't have one.""", 'error')
        return redirect(url_for("frontend.messages"))
    login_user(user)

    pending_answer = Answer.query.filter_by(state='pending',
                                            question=question,
                                            user=user).first()
    if not pending_answer:
        # then check to see if they really want to record again within the
        #   same cycle (figure out wording)
        flash(u"It appears as though you've already answered this question for today! Wait until your next email arrives, and then you can record again!")
        redirect(url_for('.show'))

    value = request.args.get("value", None)
    if value == "__TRK__":
        return render_template('track.html', question=question, user=user)

    answer = pending_answer[0]
    answer.value = value
    answer.state = 'answered'
    answer.answered_at = datetime.datetime.now()
    db.session.add(answer)
    db.session.commit()

    # TK hacky multi dispatch again
    if question.qtype == 'multi_numeric':
        flash(u"You've reported a {} out of {} for question '{}'".format(value,
                                                                         question.max_value,
                                                                         question.name), 'info')
    elif question.qtype == 'numeric':
        flash(u"You've reported a {} for question '{}'".format(value, question.name), 'info')
    elif question.qtype == 'yesno':
        flash(u"You've reported a {} for question '{}'".format('yes' if value == '0' else 'no',
                                                               question.name), 'info')
    return redirect(url_for('.show', auth_token=user.auth_token))

