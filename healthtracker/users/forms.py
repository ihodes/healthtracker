# -*- coding: utf-8 -*-
import flask
from flask.ext.wtf import Form
from wtforms import HiddenField, SelectField, IntegerField, PasswordField, TextField
from wtforms.widgets import HiddenInput
from wtforms.validators import Optional, Email, EqualTo, Required



class ScheduledQuestionForm(Form):
    id = IntegerField('id', validators=[Optional()], widget=HiddenInput())
    user_id = HiddenField('user_id')
    question_id = HiddenField('question_id')
    notification_method = SelectField('notification_method',
                                      choices=[('none', 'None'), ('email', 'Email')],
                                      validators=[Optional()])
    scheduled_for = TextField('scheduled_for', default="20:00", validators=[Optional()])


class LoginForm(Form):
    password = PasswordField('password')
    email = TextField('email', validators=[Email()])


class PasswordForm(Form):
    password = PasswordField('Password', [Required(), EqualTo('confirm', message='Passwords must match.')])
    confirm = PasswordField('Repeat Password')
