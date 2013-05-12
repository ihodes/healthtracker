from healthtracker.app import create_app
from healthtracker.users.models import User
import healthtracker.mailer as mailer

if __name__ == '__main__':
    app = create_app()
    with app.test_request_context():
        for user in User.query.filter_by(is_confirmed=True, is_approved=True).all():
            for question in user.questions:
                mailer.send_update_email(user, question)
                app.logger.info("Sent <Question::{}> to {}.".format(question.name, user.email))
