# -*- coding: utf-8 -*-
from flask import Flask, session, render_template

from .extensions import db
from .utils import format_date


# Blueprints
from .frontend import frontend
from .users import user
from .tracker import tracker
from .sms import sms



__all__ = ['create_app']

BLUEPRINTS = (frontend, user, tracker, sms,)


def create_app():
    app = Flask(__name__)
    app.config.from_object('config')

    _initialize_hooks(app)
    _initialize_extensions(app)
    _initialize_blueprints(app)
    _initialize_error_handlers(app)
    _initialize_logging(app)
    _initialize_template_filters(app)
    return app


def _initialize_hooks(app):
    @app.before_request
    def before_request():
        pass


def _initialize_extensions(app):
    db.init_app(app)


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
    def format_date(value):
        return pretty_date(value)
