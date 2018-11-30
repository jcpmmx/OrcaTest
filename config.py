# coding=utf-8


import os
from enum import Enum

from flask_cors import CORS
from sqlalchemy.exc import ProgrammingError

from app.models import TODOList


class Env(Enum):
    """
    Enum that stores all possible envs.
    """
    DEVELOPMENT = 'development'
    TESTING = 'testing'
    PRODUCTION = 'production'


class BaseConfig(object):
    """
    Default configurations for all envs.
    """
    DEBUG = True
    TESTING = True
    SECRET_KEY = os.getenv('SECRET_KEY')
    CSRF_ENABLED = True
    SQLALCHEMY_DATABASE_URI = 'postgresql://localhost/orca'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CORS_ORIGINS = ['http://localhost:3000']

    DEFAULT_TODO_LIST_NAME = '__master__'


class DevelopmentConfig(BaseConfig):
    """
    Development-only configurations.
    """
    ENV = Env.DEVELOPMENT


class TestingConfig(BaseConfig):
    """
    Testing-only configurations.
    """
    ENV = Env.TESTING
    SQLALCHEMY_DATABASE_URI = 'postgresql://localhost/orca_test'


class ProductionConfig(BaseConfig):
    """
    Production-only configurations.
    """
    ENV = Env.PRODUCTION
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    CORS_ORIGINS = BaseConfig.CORS_ORIGINS + ['https://todo-jcpmmx-reactcli.herokuapp.com']


def configure_app(app, target_env):
    """
    Sets all configurations in the given Flask app using a valid target environment (given either as a str or as a valid
    Env value).
    """
    _CONFIG_ENV_MAPPING = {
        Env.DEVELOPMENT: DevelopmentConfig,
        Env.TESTING: TestingConfig,
        Env.PRODUCTION: ProductionConfig,
    }
    if isinstance(target_env, str):
        try:
            target_env = Env(target_env)
        except ValueError:
            target_env = Env.DEVELOPMENT

    config_obj = _CONFIG_ENV_MAPPING[target_env]
    app.config.from_object(config_obj)
    CORS(app, resources=r'/api/todoitems', origins=app.config['CORS_ORIGINS'])


def configure_db(app, db):
    """
    Links together the given Flask app and the SQLAlchemy instance.
    It also loads some initial data.
    """
    db.init_app(app)
    with app.app_context():
        load_initial_db_data(app, db)


def load_initial_db_data(app, db):
    """
    Loads all required initial data to the given DB.
    """
    # Checking if we have the default TODO list
    try:
        default_todolist_data = {'name': app.config['DEFAULT_TODO_LIST_NAME']}
        if not TODOList.query.filter_by(**default_todolist_data).first():
            default_todolist = TODOList(**default_todolist_data)
            default_todolist.save()
    except ProgrammingError:
        pass  # DB is empty, no tables yet