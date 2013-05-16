# -*- coding: utf-8 -*-
from flask import (Blueprint, render_template, redirect, url_for, request, flash,
                   current_app)
import pytz

from ..database import User, Question, ScheduledQuestion
from ..extensions import db
from ..utils import format_date, is_valid_email
from ..view_helpers import (get_user_by_auth, get_user_by_id,
                            require_admin, provide_user_from_auth,
                            provide_user_from_id)
from .. import mailer

from .forms import ScheduledQuestionForm


user = Blueprint('user', __name__, url_prefix='/users', template_folder='templates')


# User views:
@user.route('/sign-up', methods=['POST'])
def subscribe():
    email = request.form.get('email')
    if is_valid_email(email):
        user = User.find_by(email=email)
        if user is None:
            user = User.create(email)
            mailer.send_confirmation_email(user)
            mailer.send_simple_email("New Marion User", "email: '{}'".format(email),
                                     'isaachodes@gmail.com') # TODO TK: shouldn't hardcode admin email
            flash(u"""You've been subscribed. An email has been sent
                  to {0} with more information""".format(email), 'info')
        elif not user.is_confirmed:
            flash(("Check your email to confirm your subscription (check your "
                   "spam if you don't see it within a minute!)"),
                  'info')
            mailer.send_confirmation_email(user)
        else:
            mailer.send_login_email(user)
            flash("We've sent you a link to log in with: check your email.".format(email), 'info')
    else:
        flash("'{0}' is not a valid email address: please re-enter your email.".format(email),
              'error')
        return redirect(url_for('frontend.landing'))
    return redirect(url_for('frontend.messages'))


@user.route('/confirm-email')
@provide_user_from_auth
def confirm_email(user):
    if user is not None:
        user.confirm()
        flash(u"""We've confirmed your email address; you can expect an email
                  from us after you've been approved.""", 'info')
    return redirect(url_for('frontend.messages'))



##############################
##        Admin views      ## 
##############################

@user.route('/')
@provide_user_from_auth
def admin(admin):
    if admin is None or not admin.is_admin:
        mailer.send_admin_login()
        return "Must be administrator. (Email sent to admin)."
    users = User.query.all()
    return render_template('admin.html', users=users, auth_token=admin.auth_token)


@user.route('/<user_id>', methods=['PUT'])
@require_admin
def update(admin, user_id=None):
    user = User.query.get(user_id)
    user.name = request.values['name']
    user.timezone = request.values['timezone']
    user.notes = request.values['notes']
    db.session.add(user)
    db.session.commit()
    return ''


@user.route('/<user_id>/toggle_approve', methods=['POST'])
@require_admin
def toggle_approve(admin, user_id=None):
    user = User.query.get(user_id)
    if user.is_approved:
        user.unapprove()
    else:
        if not user.is_confirmed:
            user.confirm()
        user.approve()
        mailer.send_approval_email(user)
    return redirect(url_for('.admin', auth_token=admin.auth_token))


@user.route('/<user_id>/reset_auth', methods=['POST'])
@require_admin
def reset_auth(admin, user_id=None):
    user = User.query.get(user_id)
    user.reset_auth_token()
    return redirect(url_for('.admin', auth_token=admin.auth_token))


@user.route('/<user_id>', methods=['DELETE'])
@require_admin
def delete(admin, user_id=None):
    user = User.query.get(user_id)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('.admin', auth_token=admin.auth_token))


@user.route('/<user_id>/send_update_email', methods=['POST'])
@require_admin
def update_email(admin, user_id=None):
    user = User.query.get(user_id)
    for sq in user.scheduled_questions:
        if sq.notification_method == 'email': # TK TODO make this right...
            mailer.send_update_email(user, sq.question)
    return redirect(url_for('.admin', auth_token=admin.auth_token))


@user.route('/unsubscribe')
@provide_user_from_auth
def unsubscribe(user):
    if user is None:
        flash(u"""Use the unsubscribe link from your newest email to unsubscribe (this link has expired!)""", 'error')
    else:
        user.unconfirm()
        flash(u"""You've been unsubscribed: we're sorry to see you go.""", 'info')
    return redirect(url_for('frontend.messages'))


@user.route('/<user_id>/edit')
@require_admin
def edit(admin, user_id=None):
    user = User.query.filter_by(id=user_id).first()
    questions = Question.query.all()
    timezones = pytz.country_timezones('US')
    NOTIFICATIONS = ['none', 'email']
    return render_template('edit.html', user=user, questions=questions,
                           auth_token=admin.auth_token, timezones=timezones,
                           notifications=NOTIFICATIONS, ScheduledQuestionForm=ScheduledQuestionForm)


@user.route('/<user_id>/scheduled_question', methods=['POST', 'PUT', 'DELETE'])
@require_admin
def scheduled_question(admin, user_id=None):
    user = User.query.get(user_id)
    form = ScheduledQuestionForm()

    if request.method == 'DELETE':
        sq_id = request.values.get('scheduled_question_id')
        scheduled_question = ScheduledQuestion.query.get(sq_id)
        db.session.delete(scheduled_question)
        db.session.commit()
        return ''
    elif request.method == 'POST' and form.validate():
        scheduled_question = ScheduledQuestion()
        form.populate_obj(scheduled_question)
        scheduled_question.id = None
        db.session.add(scheduled_question)
        db.session.commit()
    elif request.method == 'PUT' and form.validate():
        scheduled_question = ScheduledQuestion.query.get_or_404(request.form.get('id'))
        form.populate_obj(scheduled_question)
        db.session.add(scheduled_question)
        db.session.commit()

    return redirect(url_for('.edit', user_id=user_id, auth_token=admin.auth_token))
