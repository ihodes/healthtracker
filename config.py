import os

ENVIRONMENT=os.environ.get('ENVIRONMENT', 'DEVELOPMENT')

SECRET_KEY=os.environ.get('SECRET_KEY')
HOST=os.environ.get('HOST')
HOST_NAME=os.environ.get('HOST_NAME')
PORT=int(os.environ.get('PORT'))

SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL')
MAILGUN_API_KEY=os.environ.get('MAILGUN_API_KEY')
SEGMENTIO_API_KEY=os.environ.get('SEGMENTIO_API_KEY')

DEBUG=os.environ.get('DEBUG', False)
ADMIN_EMAIL=os.environ.get('ADMIN_EMAIL')

del os
