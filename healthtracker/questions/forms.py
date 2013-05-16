# -*- coding: utf-8 -*-
import flask
from flask.ext.wtf import Form
from wtforms import TextField, IntegerField, validators



class QuestionForm(Form):
    name = TextField('name')
    text = TextField('text')
    max_value = IntegerField('max_value', validators=[validators.Optional()])
    min_value = IntegerField('min_value', validators=[validators.Optional()])
