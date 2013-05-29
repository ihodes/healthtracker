# -*- coding: utf-8 -*-
import flask
from flask import (Blueprint, render_template, redirect, url_for, request, flash,
                   current_app)
from flask.views import MethodView
from flask.ext.login import current_user

import datetime

from ..database import Question, ScheduledQuestion
from ..extensions import db
from ..view_helpers import (login_required, register_api)

from .forms import QuestionForm



question = Blueprint('question', __name__, url_prefix='/questions',
                     template_folder='templates')


class QuestionAPI(MethodView):
    decorators = [login_required]

    def get(self, question_id=None):
        if not current_user.is_admin:
            flash('Cannot access.', 'error')
            return redirect(url_for('frontend.messages'))
        form = QuestionForm()
        if question_id:
            question = Question.query.get(question_id)
            return render_template('edit.html', question=question)
        questions = Question.query.all()
        return render_template('index.html', questions=questions, form=form)

    def post(self):
        form = QuestionForm()
        if form.validate():
            question = Question()
            form.populate_obj(question)
            db.session.add(question)
            db.session.commit()
            # TK HACK
            sq = ScheduledQuestion()
            sq.user_id = current_user.id
            sq.question_id = question.id
            sq.scheduled_for = datetime.time(20)
            sq.notification_method = 'none'
            db.session.add(sq)
            db.session.commit()
            # /hack
            flash("Created question: {}.".format(question.name), 'info')
        else:
            flash('Errors: ' + str(form.errors), 'error')
        return redirect(request.values.get('next') or url_for('.question_api'))

    def delete(self, admin, question_id=None):
        if not current_user.is_admin:
            flash('Cannot access.', 'error')
            return redirect(url_for('frontend.messages'))
        question = Question.query.get(question_id)
        db.session.delete(question)
        db.session.commit()
        flash("Deleted question: {}.".format(question.name), 'info')
        return ''

    # def put(self, admin, question_id=None):
    #     # TK TODO: implement (after WTForms...)
    #     pass
        

register_api(question, QuestionAPI, 'question_api', '/', pk='question_id')
