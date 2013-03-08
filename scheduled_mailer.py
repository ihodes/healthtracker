from healthtracker.database import User
from healthtracker.mailer import send_status_update_email

if __name__ == '__main__':
    for user in User.query.filter_by(is_confirmed=True, is_approved=True).all():
        send_status_update_email(user)
