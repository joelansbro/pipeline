"""
Database, Flask and Scheduler configuration
"""
from os import environ, path
from dotenv import load_dotenv

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, ".env"))

SQLALCHEMY_DATABASE_URI = environ.get("SQLALCHEMY_DATABASE_URI")

CLEANUP_DATA = False


CELERY_BROKER = environ.get("CELERY_BROKER")
CELERY_BACKEND = environ.get("CELERY_BACKEND")

