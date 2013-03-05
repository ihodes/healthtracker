import os

SECRET_KEY=os.environ.get("SECRET_KEY")
DATABASE_URI=os.environ.get("HEROKU_POSTGRESQL_AMBER_URL")
HOST=os.environ.get("HOST")
PORT=int(os.environ.get("PORT"))

DEBUG=os.environ.get("DEBUG", False)

del os
