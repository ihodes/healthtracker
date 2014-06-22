# -*- coding: utf-8 -*-
import datetime
import pytz
import collections
import itertools as it

from healthtracker.app import create_app
from healthtracker.database import User, ScheduledQuestion, Answer
from healthtracker.extensions import db
import healthtracker.mailer as mailer



def to_utc(timestamp):
    return datetime.datetime(year=timestamp.year, month=timestamp.month,
                             day=timestamp.day, hour=timestamp.hour,
                             minute=timestamp.minute,
                             tzinfo=pytz.timezone('UTC'))


def ask_quietly(user, questions):
    '''Pending answers are created for each question,
    but the user is not notified.
    '''
    if questions:
        for question in questions:
            Answer.pend(user, question)


def notify(user, questions):
    # TK TODO: eventually, dispatch these to a MQ
    # sms.ask(user, questions['text'])
    mailer.ask(user, questions.get('email'))
    ask_quietly(user, questions.get('none'))


def main():
    app = create_app()
    ctx = app.test_request_context()
    ctx.push()

    now = to_utc(datetime.datetime.now())
    for user in User.query.filter_by(is_confirmed=True, is_approved=True).all():
        try:
            user_tz = pytz.timezone(user.timezone)
        except:
            user_tz = pytz.timezone('UTC')
        adj_time_now = datetime.time(now.astimezone(user_tz).hour)
        scheduled_questions = ScheduledQuestion.query.filter_by(user=user,
                                                                scheduled_for=adj_time_now).all()
        questions = collections.defaultdict(list)
        for sq in scheduled_questions:
            questions[sq.notification_method].append(sq.question)
        notify(user, questions)

    ctx.pop()


if __name__ == '__main__':
    main()
