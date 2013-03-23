from healthtracker import app
from healthtracker.database import User
import healthtracker.mailer as mailer

if __name__ == '__main__':
    with app.test_request_context():
        for user in User.query.filter_by(is_confirmed=True, is_approved=True).all():
            mailer.send_status_update_email(user)
            app.logger.info("Sent status update to {}.".format(user.email))
