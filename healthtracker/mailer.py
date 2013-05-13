# -*- coding: utf-8 -*-
import requests
from flask import render_template, current_app

from .users import User



API_ENDPOINT = "https://api.mailgun.net/v2/healthtracker.mailgun.org/messages"
DEFAULT_FROM = "Marion Health <hello@healthtracker.mailgun.org>"


def send_email(**kwargs):
    admin_email = current_app.config['ADMIN_EMAIL']
    data = {'to': kwargs.get('to', admin_email),
            'from': kwargs.get('from', DEFAULT_FROM),
            'subject': kwargs.get('subject'),
            'text': kwargs.get('text', '')}

    current_app.logger.info("Sending email '{}' to {}".format(data['subject'], data['to']))
    if current_app.config['ENVIRONMENT'] != 'PRODUCTION':
        data['to'] = admin_email

    html = kwargs.get('html')
    if html:
        data = dict(data, html=html)
    if data['subject'] is None:
        data['subject'] = data['text'][10:]

    return requests.post(API_ENDPOINT, auth=('api', current_app.config['MAILGUN_API_KEY']), data=data)


def send_admin_login():
    subject = "Marion Health admin"
    admin = User.query.filter_by(email=current_app.config['ADMIN_EMAIL'])[0]
    text = "click to login: http://{0}/users/?auth_token={1}".format(current_app.config['HOST_NAME'], admin.auth_token)
    current_app.logger.info("Sending admin login email to admin.")
    send_email(text=text, subject=subject)


def send_login_email(user):
    subject = "Marion Health Login"
    text = "Click to login: http://{0}/tracker/track?auth_token={1}".format(current_app.config['HOST_NAME'], user.auth_token)
    send_email(text=text, to=user.email, subject=subject)


def send_update_email(user, question):
    subject = "Update Your Health Today"
    
    unsubscribe_link = unsubscribe_url(user)
    status_update_text = []
    status_update_text.append(question.text)
    status_update_links = []
    for value in range(6): # this is not ideal (e.g. how many pushups did you do today: 0-6?)
        status_update_link = status_update_url(user, value)
        status_update_links.append(status_update_link)
        status_update_text.append("{0}: {1}".format(value, status_update_link))
    status_update_text.append("\n\n\n Unsubscribe: "+unsubscribe_link)
    text = "\n\n".join(status_update_text)
    html = render_template('emails/status_update.html',
                                status_update_links=status_update_links,
                                unsubscribe_link=unsubscribe_link)

    send_email(text=text, to=user.email, subject=subject, html=html)


def send_confirmation_email(user):
    subject = "Marion Health Email Confirmation "
    text = """
Thank you for signing up to Marion Health! Please confirm that this is your email address, and we'll try to approve you as soon as possible. We're in early Alpha right now, so we're letting people in very slowly for now.
                 
Click to confirm your email address: http://{0}/users/confirm-email?auth_token={1}

If you didn't signed up for getMarion.com, please ignore this email""".format(current_app.config['HOST_NAME'], user.auth_token)
    send_email(text=text, to=user.email, subject=subject)


def send_approval_email(user):
    email_subject = "Marion Health Account Approval "
    text = """You've been approved to join the Marion Health alpha test! Thank you for your patience. You will be recieving an email from us today or tomorrow asking for your first status update.

Sincerely, 
Isaac Hodes

Founder, Marion Health""".format(current_app.config['HOST_NAME'], user.auth_token)
    send_email(text=text, to=user.email, subject=subject)


def send_simple_email(subject, message, email):
    send_email(text=message, to=email, subject=subject)


def status_update_url(user, value):
    url_base = "http://{0}/tracker/track?auth_token={1}&value={2}"
    auth = user.auth_token
    return url_base.format(current_app.config['HOST_NAME'], auth, value)


def unsubscribe_url(user):
    url_base = "http://{0}/users/unsubscribe?auth_token={1}"
    auth = user.auth_token
    return url_base.format(current_app.config['HOST_NAME'], auth)
