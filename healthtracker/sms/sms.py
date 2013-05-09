# -*- coding: utf-8 -*-
from flask import Blueprint, request
from flask import current_app as APP
import twilio.twiml



sms = Blueprint('sms', __name__, url_prefix='/sms')

 
@sms.route("/sms/record", methods=['GET', 'POST'])
def sms_record():
    """Respond to incoming calls with a simple text message."""
 
    resp = twilio.twiml.Response()
    body = request.form.get('Body', None)
    if body == "test":
        resp.sms("Good afternoon, Isaac. We hope you're feeling well today. How do you feel, on a scale of 0-5?")
        return str(resp)
    else:
        resp.sms("You reported a "+body+". We hope you feel better soon! Text OOPS to re-record, or visit getmarion.com.")
        return str(resp)
