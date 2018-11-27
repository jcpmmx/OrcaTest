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
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')


def configure_app(app, target_env):
    """
    Sets all configurations in the given Flaks app using a valid target environment.
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
