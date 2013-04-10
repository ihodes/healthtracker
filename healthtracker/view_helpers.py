# -*- coding: utf-8 -*-
from functools import wraps

from flask import redirect, url_for, request

from healthtracker.db import Patient, Provider



def get_patient_by_auth(request):
    auth_token = request.form.get('auth_token', None)
    if auth_token is None:
        auth_token = request.args.get('auth_token', None)
    patient = Patient.query.filter_by(auth_token=auth_token).first()
    return patient


def get_patient_by_id(request):
    patient_id = request.args.get('patient_id', None)
    if patient_id is None:
        patient_id = request.form.get('patient_id', None)
    patient = Patient.query.filter_by(id=patient_id).first()
    return patient


def require_admin(view):
    @wraps(view)
    @provide_patient_from_auth
    def secured_view(patient, *args, **kwargs):
        if patient is None or not patient.is_admin:
            flash(u"""Need to be admin to log in""".format(email), "error")
            return redirect(url_for("messages"))
        args = (patient,) + args
        return view(*args, **kwargs)
    return secured_view


def provide_patient_from_auth(view):
    @wraps(view)
    def decorated_view(*args, **kwargs):
        patient = get_patient_by_auth(request)
        args = (patient,) + args
        return view(*args, **kwargs)
    return decorated_view


def provide_patient_from_id(view):
    @wraps(view)
    def decorated_view(*args, **kwargs):
        patient = get_patient_by_id(request)
        args = (patient,) + args
        return view(*args, **kwargs)
    return decorated_view
