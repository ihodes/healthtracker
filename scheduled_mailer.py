import datetime 
import pytz 

from healthtracker.app import create_app
from healthtracker.database import User
import healthtracker.mailer as mailer

if __name__ == '__main__':
    app = create_app()
    now = datetime.datetime.now()

    with app.test_request_context():
        for user in User.query.filter_by(is_confirmed=True, is_approved=True).all():
            time_now = datetime.datetime(year=now.year, month=now.month,
                                         day=now.day, hour=now.hour, minute=now.minute,
                                         tzinfo=pytz.timezone('UTC'))
            try:
                user_tz = pytz.timezone(user.timezone)
            except pytz.exceptions.UnknownTimeZoneError:
                app.logger.info('\tNo timezone for user, assuming UTC')
                user_tz = pytz.timezone('UTC')
            adj_time_now = datetime.time(time_now.astimezone(user_tz).hour) # UTC -> user's timezone

            for sq in user.scheduled_questions:
                if sq.scheduled_for == adj_time_now:
                    if sq.notification_method == 'email':
                        mailer.send_update_email(user, sq.question)
                        app.logger.info("Emailed <Question::{}> to {}.".format(sq.question.name, user.email))
