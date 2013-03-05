# -*- coding: utf-8 -*-

from healthtracker import app
from healthtracker.database import User

def send_admin_login():
    api_endpoint = "https://api.mailgun.net/v2/healthtracker.mailgun.org/messages"
    api_key = app.config["MAILGUN_API_KEY"]
    from_email = "Health Tracker <hello@healthtracker.mailgun.org>"
    email_subject = "HealthTracker admin"

    user = User.query.filter_by(email="isaachodes@gmail.com").first()

    email_text = "click to login: http://{0}/admin?auth_token={1}".format(HOST, user.auth_token)

    return requests.post(api_endpoint,
                         auth=("api", api_key),
                         data={"from": from_email,
                               "to": "isaachodes@gmail.com",
                               "subject": email_subject,
                               "text": email_text})
