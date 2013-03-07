# -*- coding: utf-8 -*-
from functools import wraps

from flask import redirect, url_for, request

from healthtracker.database import User


def get_user_by_auth(request):
    param_auth_token = request.args.get('auth_token', None)
    form_auth_token = request.form.get('auth_token', None)
    user = None
    
    if param_auth_token:
        user = User.query.filter_by(auth_token=param_auth_token).first()
    elif form_auth_token:
        user = User.query.filter_by(auth_token=form_auth_token).first()

    return user


def get_user_by_id(request):
    param_user_id = request.args.get('user_id', None)
    form_user_id = request.form.get('user_id', None)
    user = None
    
    if param_user_id:
        user = User.query.filter_by(id=param_user_id).first()
    elif form_user_id:
        user = User.query.filter_by(id=form_user_id).first()

    return user


def admin_required(view):
    @wraps(view)
    def secured_view(*args, **kwargs):
        user = get_user_by_auth(request)
        if user is None or not user.is_admin:
            flash(u"""Need to be admin to log in""".format(email), "error")
            return redirect(url_for("index"))
        args = args + tuple([user])
        return view(*args, **kwargs)

    return secured_view

