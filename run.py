# condig=utf-8


import os

from app import create_app
from config import Env

app = create_app(os.getenv('FLASK_ENV', Env.DEVELOPMENT))

if __name__ == '__main__':
    app.run()