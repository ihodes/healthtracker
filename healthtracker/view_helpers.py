# -*- coding: utf-8 -*-
from functools import wraps

from flask import redirect, url_for, request

from .users.models import User



def get_user_by_auth(request):
    auth_token = request.form.get('auth_token', None)
    if auth_token is None:
        auth_token = request.args.get('auth_token', None)
    user = User.query.filter_by(auth_token=auth_token).first()
    return user


def get_user_by_id(request):
    user_id = request.args.get('user_id', None)
    if user_id is None:
        user_id = request.form.get('user_id', None)
    user = User.query.filter_by(id=user_id).first()
    return user


def require_admin(view):
    @wraps(view)
    @provide_user_from_auth
    def secured_view(user, *args, **kwargs):
        if user is None or not user.is_admin:
            flash(u"""Need to be admin to log in""".format(email), "error")
            return redirect(url_for("messages"))
        args = (user,) + args
        return view(*args, **kwargs)
    return secured_view


def provide_user_from_auth(view):
    @wraps(view)
    def decorated_view(*args, **kwargs):
        user = get_user_by_auth(request)
        args = (user,) + args
        return view(*args, **kwargs)
    return decorated_view


def provide_user_from_id(view):
    @wraps(view)
    def decorated_view(*args, **kwargs):
        user = get_user_by_id(request)
        args = (user,) + args
        return view(*args, **kwargs)
    return decorated_view
