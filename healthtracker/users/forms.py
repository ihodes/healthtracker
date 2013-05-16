# -*- coding: utf-8 -*-
import flask
from flask.ext.wtf import Form
from wtforms import HiddenField, SelectField, IntegerField
from wtforms.widgets import HiddenInput
from wtforms.validators import Optional



class ScheduledQuestionForm(Form):
    id = IntegerField('id', validators=[Optional()], widget=HiddenInput())
    user_id = HiddenField('user_id')
    question_id = HiddenField('question_id')
    notification_method = SelectField('notification_method',
                                      choices=[('none', 'None'), ('email', 'Email')],
                                      validators=[Optional()])
        
