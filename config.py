import os

SECRET_KEY=':\x90[\xf2F[X\xcbA\xcbA\xcf\xd7U3\xdb+/b\xf0\x1f\xe9\x00\xe4'
DEBUG=True
DATABASE_URI=os.environ.get("HEROKU_POSTGRESQL_AMBER_URL", 'sqlite:///dev.db')
HOST=os.environ.get("HOST", "0.0.0.0")
PORT=int(os.environ.get('PORT', 5000))

del os
