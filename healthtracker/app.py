# -*- coding: utf-8 -*-
from flask import Flask, session, render_template, current_app
from flask.ext.login import current_user
from werkzeug import url_decode
import pytz
from datetime import datetime


from .extensions import db, lm
from .middleware import MethodRewriteMiddleware
from .utils import localized_date
from .database import User

# Blueprints
from .frontend import frontend
from .users import user
from .tracker import tracker
from .questions import question



BLUEPRINTS = (frontend, user, tracker, question)


def create_app():
    app = Flask(__name__)

    _initialize_config(app)
    _initialize_middleware(app)
    _initialize_hooks(app)
    _initialize_extensions(app)
    _initialize_blueprints(app)
    _initialize_error_handlers(app)
    _initialize_logging(app)
    _initialize_template_filters(app)
    
    return app


def _initialize_config(app):
    app.config.from_object('config')


def _initialize_middleware(app):
    app.wsgi_app = MethodRewriteMiddleware(app.wsgi_app)


def _initialize_hooks(app):
    # @app.before_request
    # def before_request():
    #     pass
    pass


def _initialize_extensions(app):
    db.init_app(app)
    lm.init_app(app)

    @lm.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @lm.token_loader
    def load_token(token):
        return User.query.get(int(token))


def _initialize_blueprints(app):
    for blueprint in BLUEPRINTS:
        app.register_blueprint(blueprint)


def _initialize_error_handlers(app):
    @app.errorhandler(404)
    def not_found(error):
        return render_template('errors/404.html'), 404


def _initialize_logging(app):
    pass


def _initialize_template_filters(app):
    @app.template_filter()
    def fmt_time(dt):
        now = datetime.now()
        dt = datetime(now.year, now.month, now.day, dt.hour, dt.minute, dt.second, dt.microsecond)
        ds = dt.strftime("%I:%M %p")
        return ds.lstrip('0')
