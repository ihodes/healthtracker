# -*- coding: utf-8 -*-
from flask import Flask, session, render_template
from werkzeug import url_decode

from .extensions import db
from .utils import format_date

# Blueprints
from .frontend import frontend
from .users import user
from .tracker import tracker
from .sms import sms
from .questions import question



BLUEPRINTS = (frontend, user, tracker, sms, question)


def create_app():
    app = Flask(__name__)

    _initialize_config(app)
    _initialize_hooks(app)
    _initialize_extensions(app)
    _initialize_blueprints(app)
    _initialize_error_handlers(app)
    _initialize_logging(app)
    _initialize_template_filters(app)
    
    app.wsgi_app = MethodRewriteMiddleware(app.wsgi_app)
    return app


def _initialize_config(app):
    app.config.from_object('config')


def _initialize_hooks(app):
    # @app.before_request
    # def before_request():
    #     pass
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



class MethodRewriteMiddleware(object):
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        if 'METHOD_OVERRIDE' in environ.get('QUERY_STRING', ''):
            args = url_decode(environ['QUERY_STRING'])
            method = args.get('__METHOD_OVERRIDE__')
            if method:
                method = method.encode('ascii', 'replace')
                environ['REQUEST_METHOD'] = method
        return self.app(environ, start_response)
