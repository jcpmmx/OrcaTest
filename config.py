# coding=utf-8


import os
from enum import Enum


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


def configure_app(app, config_name):
    """
    Adds all configurations from `config_name` to the given Flask app, if any.
    """
    _APP_CONFIG = {
        Env.DEVELOPMENT: DevelopmentConfig,
        Env.TESTING: TestingConfig,
        Env.PRODUCTION: ProductionConfig,
    }
    config_obj = _APP_CONFIG.get(config_name)
    if not config_obj:
        raise ValueError('Invalid configuration profile name: {}'.format(config_name))

    app.config.from_object(config_obj)
