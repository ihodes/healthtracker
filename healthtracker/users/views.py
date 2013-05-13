# -*- coding: utf-8 -*-
from flask import (Blueprint, render_template, redirect, url_for, request, flash,
                   current_app)
import pytz

from .models import User
from ..questions.models import Question
from ..extensions import db
from ..utils import format_date, is_valid_email
from ..view_helpers import (get_user_by_auth, get_user_by_id,
                            require_admin, provide_user_from_auth,
                            provide_user_from_id)
from .. import mailer



user = Blueprint('user', __name__, url_prefix='/users',
                 template_folder='templates')


# User views:
@user.route('/sign-up', methods=['POST'])
def subscribe():
    email = request.form.get('email')
    if is_valid_email(email):
        user = User.find_by(email=email)
        if user is None:
            user = User.create(email)
            mailer.send_confirmation_email(user)
            mailer.send_simple_email("New Marion User", "email: '{}'".format(email), 'isaachodes@gmail.com') # TODO TK: shouldn't hardcode admin email
            flash(u"""You've been subscribed. An email has been sent
                  to {0} with more information""".format(email), 'info')
        elif not user.is_confirmed:
            flash(u"""Check your email to confirm your subscription (check your spam if you don't see it within a minute!)""", 'info')
            mailer.send_confirmation_email(user)
        else:
            mailer.send_login_email(user)
            flash(u"""We've sent you a link to log in with: check your email.""".format(email), 'info')
    else:
        flash(u""""{0}" is not a valid email address:
              please re-enter your email.""".format(email), 'error')
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


@user.route('/<user_id>/edit')
@require_admin
def edit(admin, user_id=None):
    user = User.query.filter_by(id=user_id).first()
    questions = Question.query.all()
    timezones = pytz.country_timezones('US')
    return render_template('edit.html', user=user, questions=questions, auth_token=admin.auth_token, timezones=timezones)


@user.route('/<user_id>', methods=['PUT'])
@require_admin
def update(admin, user_id=None):
    user = User.query.filter_by(id=user_id).first()
    user.name = request.values['name']
    user.timezone = request.values['timezone']
    user.notes = request.values['notes']
    db.session.add(user)
    db.session.commit()
    return ''


@user.route('/toggle_approve', methods=['POST'])
@require_admin
@provide_user_from_id
def toggle_approve(user, admin):
    if user.is_approved:
        user.unapprove()
    else:
        if not user.is_confirmed:
            user.confirm()
        user.approve()
        mailer.send_approval_email(user)
    return redirect(url_for('.admin', auth_token=admin.auth_token))


@user.route('/delete', methods=['POST'])
@require_admin
@provide_user_from_id
def delete(user, admin):
    user.delete()
    return redirect(url_for('.admin', auth_token=admin.auth_token))


@user.route('/reset_auth', methods=['POST'])
@require_admin
@provide_user_from_id
def reset_auth(user, admin):
    user.reset_auth_token()
    return redirect(url_for('.admin', auth_token=admin.auth_token))


@user.route('/<user_id>/send_update_email', methods=['POST'])
@require_admin
def update_email(admin, user_id=None):
    user = User.query.get(user_id)
    questions = user.questions
    for question in user.questions:
        mailer.send_update_email(user, question)
    return redirect(url_for('.admin', auth_token=admin.auth_token))


@user.route('/unsubscribe')
@provide_user_from_auth
def unsubscribe(user):
    if user is None:
        flash(u"""Use the unsubscribe link from your newest email to unsubscribe (this link has expired!)""", 'error')
    else:
        user.unconfirm()
        flash(u"""You've been unsubscribed: we're sorry to see you go.""", 'info')
    return redirect('frontend.messages') # TODO need to use url_for correctly here... 


@user.route('/question', methods=['DELETE', 'POST'])
@require_admin
def question(admin):
    user = User.query.get(request.values['user_id'])
    question = Question.query.get(request.values['question_id'])
    if request.method == 'POST':
        user.questions.append(question)
        db.session.add(user)
        db.session.commit()
        return ''
    else:
        user.questions.remove(question)
        db.session.add(user)
        db.session.commit()
        return ''

