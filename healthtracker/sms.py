# -*- coding: utf-8 -*-

import twilio.twiml
from flask import render_template, current_app, redirect, request

from .database import User



SMS_LENGTH = 160

def ask(user, questions):
    # TK TODO
    # create array to add to redis, so we know which order to register answer values on answers
    # e.g. Text msg: Question 1? Question 2? Question 3?
    #      Answer: 13, yes, 7.5
    # then Question 1 gets 13, Q2 gets yes, Q3 gets 7.5
    # (or errors, etc)

    text = ''
    for question in questions:
        if len(question.text + text) < SMS_LENGTH:
            text += question.text
        else:
            send_text(user, text)
            text = ''
    if text:
            send_text(user, text)


def send_text(user, text):
    pass
