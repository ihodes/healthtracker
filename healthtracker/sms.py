# -*- coding: utf-8 -*-

# TK TODO module


import twilio.twiml
from flask import render_template, current_app, redirect, request

from .database import User



SMS_LENGTH = 160

def ask(user, questions):
    text = ""
    for q in questions:
        if len(text) < (SMS_LENGTH - 20):
    while 
        text += question.text

