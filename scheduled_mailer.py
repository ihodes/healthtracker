from healthtracker.app import create_app
from healthtracker.database import User
import healthtracker.mailer as mailer

if __name__ == '__main__':
    app = create_app()
    with app.test_request_context():
        for user in User.query.filter_by(is_confirmed=True, is_approved=True).all():
            user.reset_auth_token()
            for sq in user.scheduled_questions:
                if sq.notification_method == 'email':
                    mailer.send_update_email(user, sq.question)
                    app.logger.info("Sent <Question::{}> to {}.".format(question.name, user.email))
