from healthtracker.database import User
from healthtracker.mailer import send_status_update_email

if __name__ == '__main__':
    for user in User.query.all():
        send_status_update_email(user)
