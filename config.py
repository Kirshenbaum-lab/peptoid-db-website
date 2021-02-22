import os
basedir = os.path.abspath(os.path.dirname(__file__))

# SQL Alchemy configure from object


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PEPTOIDS_PER_PAGE = 6
    BASIC_AUTH_USERNAME = 'admin'
    BASIC_AUTH_PASSWORD = 'password'
