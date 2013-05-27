# -*- coding: utf-8 -*-
from flask import (Blueprint, render_template, redirect, url_for, request, flash,
                   current_app)
from flask.ext.login import login_required, login_user, logout_user, current_user
from flask.ext.bcrypt import generate_password_hash
import pytz

from ..database import User, Question, ScheduledQuestion
from ..extensions import db
from ..utils import is_valid_email
from ..view_helpers import (get_user_by_auth, get_user_by_id,
                            admin_required, require_admin, provide_user_from_auth,
                            provide_user_from_id)
from .. import mailer

from .forms import ScheduledQuestionForm, LoginForm, PasswordForm
from ..questions.forms import QuestionForm


user = Blueprint('user', __name__, url_prefix='/users', template_folder='templates')


@user.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_active(): return redirect(url_for('.home'))
    form = LoginForm()
    if request.method == 'POST':
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            if user.check_password(form.password.data):
                login_user(user)
                flash("You've been logged in.")
                return redirect(request.args.get('next') or url_for('.home'))
        flash(u"Invalid credentials. Please check your email and password.")
    return render_template('login.html', login_form=form)


@user.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You've been logged out.")
    return redirect(url_for('frontend.landing'))


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


@user.route('/unsubscribe')
@provide_user_from_auth
def unsubscribe(user):
    if user is None:
        flash(u"""Use the unsubscribe link from your newest email to unsubscribe (this link has expired!)""", 'error')
    else:
        user.unconfirm()
        flash(u"""You've been unsubscribed: we're sorry to see you go.""", 'info')
    return redirect(url_for('frontend.messages'))


@user.route('/confirm-email')
@provide_user_from_auth
def confirm_email(user):
    if user is not None:
        user.confirm()
        flash(u"""We've confirmed your email address; you can expect an email
                  from us after you've been approved.""", 'info')
    return redirect(url_for('frontend.messages'))


@user.route('/home')
@login_required
def home():
    user = current_user
    password_form = PasswordForm()
    timezones = pytz.country_timezones('US')
    questions = Question.query.filter_by(is_public=True).all()
    private_questions = Question.query.filter_by(is_public=False, created_by=user.id).all()
    return render_template('home.html', user=user, timezones=timezones, questions=questions, private_questions=private_questions,
                           password_form=password_form, ScheduledQuestionForm=ScheduledQuestionForm, QuestionForm=QuestionForm)


@user.route('/feedback', methods=['POST'])
@login_required
def feedback():
    user = current_user
    feedback = request.values.get('feedback')
    mailer.send_email(**{'from':user.email, 'subject': "Feedback from {}".format(user.name or user.email),
                         'text': feedback})
    flash(u"Feedback sent–Thank you!", 'info')
    return redirect(request.values.get('next') or url_for('.home'))
    

@user.route('/<user_id>/password', methods=['PUT', 'POST'])
@login_required
def change_password(user_id=None):
    user = User.query.get(user_id)
    form = PasswordForm()
    if current_user.is_admin or current_user == user: # TK TODO should abstract these out into permissions
        if form.validate_on_submit():
            user.encrypted_password = generate_password_hash(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash("Your password has been changed.",'info')
        else:
            if form.password.errors: 
                flash(form.password.errors[0], 'error')
            else:
                current_app.logger.info(form.errors)
    return redirect(request.values.get('next') or url_for('.home'))
    


##############################
##        Admin views      ## 
##############################

@user.route('/')
@admin_required
def admin():
    users = User.query.all()
    return render_template('admin.html', users=users, auth_token=current_user.auth_token)


@user.route('/<user_id>', methods=['PUT'])
@login_required
def update(user_id=None):
    user = User.query.get(user_id)
    if current_user.is_admin or current_user == user:
        user.name = request.values['name']
        user.timezone = request.values['timezone']
        user.notes = request.values['notes']
        db.session.add(user)
        db.session.commit()
        flash("Your profile has been updated.", 'info')
        return redirect(request.values.get('next') or url_for('.home'))
    else:
        flash("Not authorized to edit this user.",'info')
        return redirect(request.values.get('next') or url_for('.home'))
    


@user.route('/<user_id>/toggle_approve', methods=['POST'])
@admin_required
def toggle_approve(admin, user_id=None):
    user = User.query.get(user_id)
    if user.is_approved:
        user.unapprove()
    else:
        if not user.is_confirmed:
            user.confirm()
        user.approve()
        mailer.send_approval_email(user)
    return redirect(url_for('.admin', auth_token=current_user.auth_token))


@user.route('/<user_id>/reset_auth', methods=['POST'])
@admin_required
def reset_auth(user_id=None):
    user = User.query.get(user_id)
    user.reset_auth_token()
    return redirect(url_for('.admin', auth_token=current_user.auth_token))


@user.route('/<int:user_id>', methods=['DELETE'])
@admin_required
def delete(user_id=None):
    user = User.query.get(user_id)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('.admin', auth_token=current_user.auth_token))


@user.route('/<user_id>/send_update_email', methods=['POST'])
@admin_required
def update_email(user_id=None):
    user = User.query.get(user_id)
    for sq in user.scheduled_questions:
        if sq.notification_method == 'email': # TK TODO make this right...
            mailer.send_update_email(user, sq.question)
    return redirect(url_for('.admin', auth_token=current_user.auth_token))


@user.route('/<user_id>/edit')
@admin_required
def edit(user_id=None):
    user = User.query.filter_by(id=user_id).first()
    questions = Question.query.all()
    timezones = pytz.country_timezones('US')
    NOTIFICATIONS = ['none', 'email']
    return render_template('edit.html', user=user, questions=questions,
                           auth_token=current_user.auth_token, timezones=timezones,
                           notifications=NOTIFICATIONS, ScheduledQuestionForm=ScheduledQuestionForm)


@user.route('/scheduled_question', methods=['POST', 'PUT'])
@login_required
def scheduled_question():
    form = ScheduledQuestionForm()
    user = User.query.get(form.data.get('user_id'))

    if not (current_user.is_admin or current_user == user):
        flash("Not authorized.",'error')
        return redirect(url_for('frontend.messages'))

    elif request.method == 'POST' and form.validate():
        scheduled_question = ScheduledQuestion()
        form.populate_obj(scheduled_question)
        current_app.logger.info(request.form)
        current_app.logger.info(form.data)
        scheduled_question.id = None
        db.session.add(scheduled_question)
        db.session.commit()
    elif request.method == 'PUT' and form.validate():
        scheduled_question = ScheduledQuestion.query.get_or_404(request.form.get('id'))
        form.populate_obj(scheduled_question)
        db.session.add(scheduled_question)
        db.session.commit()

    return redirect(url_for('.home'))


# TK SECURE: can this be CSRF'd? How to prevent this since I can't include a csrf token in a DELETE body (evidently?) query string param?
@user.route('/scheduled_question/<scheduled_question_id>', methods=['POST', 'DELETE'])
@login_required
def delete_scheduled_question(scheduled_question_id=None):
    scheduled_question = ScheduledQuestion.query.get(scheduled_question_id)

    if not (current_user.is_admin or current_user == scheduled_question.user):
        flash("Not authorized.",'error')
        return redirect(url_for('frontend.messages'))

    if request.method == 'DELETE':
        sq_id = request.values.get('scheduled_question_id')
        db.session.delete(scheduled_question)
        db.session.commit()

    return redirect(url_for('.home'))
