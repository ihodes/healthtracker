# -*- coding: utf-8 -*-
import flask
from flask import (Blueprint, render_template, redirect, url_for, request, flash,
                   current_app)
from flask.views import MethodView

from .models import Question
from ..extensions import db
from ..view_helpers import (require_admin, register_api)



question = Blueprint('question', __name__, url_prefix='/questions',
                     template_folder='templates')


class QuestionAPI(MethodView):
    decorators = [require_admin]

    def get(self, admin, question_id=None):
        if question_id:
            question = Question.query.get(question_id)
            return render_template('edit.html', question=question)
        questions = Question.query.all()
        return render_template('index.html', questions=questions, auth_token=admin.auth_token)

    def post(self, admin):
        form = request.form
        question = Question(form["name"], form["text"])
        db.session.add(question)
        db.session.commit()
        flash("Created question: {}.".format(question.name), 'info')
        return redirect(url_for('.question_api', auth_token=admin.auth_token))

    def delete(self, admin, question_id=None):
        question = Question.query.get(question_id)
        db.session.delete(question)
        db.session.commit()
        flash("Deleted question: {}.".format(question.name), 'info')
        return ''

    def put(self, admin, question_id=None):
        # TK TODO: implement (after WTForms...)
        pass
        

register_api(question, QuestionAPI, 'question_api', '/', pk='question_id')
