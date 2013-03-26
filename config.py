import os

SECRET_KEY=os.environ.get("SECRET_KEY")
HOST=os.environ.get("HOST")
HOST_NAME=os.environ.get("HOST_NAME")
PORT=int(os.environ.get("PORT"))

DATABASE_URL=os.environ.get("DATABASE_URL")
MAILGUN_API_KEY="key-25pn6z0fogz-783zc7gcloa8gs23qkq2"

DEBUG=os.environ.get("DEBUG", False)


del os
