# -*- coding: utf-8 -*-
from functools import wraps
from flask import redirect, url_for, request, flash, current_app

from .users import User



def get_user_by_auth(request):
    auth_token = request.values.get('auth_token', None)
    user = User.query.filter_by(auth_token=auth_token).first()
    return user


def get_user_by_id(request):
    user_id = request.values.get('user_id', None)
    user = User.query.filter_by(id=user_id).first()
    return user


def require_admin(view):
    @wraps(view)
    @provide_user_from_auth
    def secured_view(user, *args, **kwargs):
        if user is None or not user.is_admin:
            flash("ERROR: Not administrator.", 'error')
            return redirect(url_for('frontend.messages'))
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


def register_api(app, view, endpoint, url, pk='id', pk_type='int'):
    view_func = view.as_view(endpoint)
    app.add_url_rule(url,
                     view_func=view_func, methods=['GET',])
    app.add_url_rule(url, view_func=view_func, methods=['POST',])
    app.add_url_rule('%s<%s:%s>' % (url, pk_type, pk), view_func=view_func,
                     methods=['GET', 'PUT', 'DELETE'])

