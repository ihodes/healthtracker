# -*- coding: utf-8 -*-

import requests

from healthtracker import app
from healthtracker.database import User

def send_admin_login():
    api_endpoint = "https://api.mailgun.net/v2/healthtracker.mailgun.org/messages"
    api_key = app.config["MAILGUN_API_KEY"]
    from_email = "Health Tracker <hello@healthtracker.mailgun.org>"
    email_subject = "HealthTracker admin"

    user = User.query.filter_by(email="isaachodes@gmail.com").first()

    email_text = "click to login: http://{0}/admin?auth_token={1}".format(app.config["SERVER_NAME"], user.auth_token)

    return requests.post(api_endpoint,
                         auth=("api", api_key),
                         data={"from": from_email,
                               "to": "isaachodes@gmail.com",
                               "subject": email_subject,
                               "text": email_text})

def send_status_update_email(user):
    api_endpoint = "https://api.mailgun.net/v2/healthtracker.mailgun.org/messages"
    api_key = app.config["MAILGUN_API_KEY"]
    from_email = "Health Tracker <hello@healthtracker.mailgun.org>"
    to_email = user.email
    email_subject = "Update Your Health Today"

    status_update_links = ["Let us know how you're feeling today. \n\n 0 being the first and worst, 5 being the best."]
    for value in range(6):
        status_update_link = construct_status_update_url(user, value)
        status_update_links.append("{0}: {1}".format(value, status_update_link))

    email_text = "\n\n".join(status_update_links)
    # template = render_template('emails/status_update.html', val_links=status_update_links)

    return requests.post(api_endpoint,
                         auth=("api", api_key),
                         data={"from": from_email,
                               "to": to_email,
                               "subject": email_subject,
                               "text": email_text})


def construct_status_update_url(user, value):
    url_base = "http://{0}/tracker?auth_token={1}&value={2}"
    server_name= app.config["SERVER_NAME"]
    auth = user.auth_token
    return url_base.format(server_name, auth, value)
