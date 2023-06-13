"""File with settings and configs for the project"""
import os
from dotenv import load_dotenv

envpath = os.path.join(os.path.abspath(os.path.dirname(__file__)), '.env')
load_dotenv(envpath)

SECRET = os.environ.get("SECRET")

DB_USER = os.environ.get("POSTGRES_USER")
DB_PASS = os.environ.get("POSTGRES_PASSWORD")
DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")
DB_NAME = os.environ.get("POSTGRES_DB")

REDIS_PORT = os.environ.get("REDIS_PORT")
REDIS_HOST = os.environ.get("REDIS_HOST")
REDIS_PASS = os.environ.get("REDIS_PASS")

EMAIL_ADDRESS = os.environ.get("EMAIL_ADDRESS")
EMAIL_PASS = os.environ.get("EMAIL_PASS")

ACCESS_KEY_ID = os.environ.get("ACCESS_KEY_ID")
SECRET_ACCESS_KEY = os.environ.get("SECRET_ACCESS_KEY")
BUCKET_NAME = os.environ.get("BUCKET_NAME")

APP_HOST = os.environ.get("APP_HOST")
APP_PORT = os.environ.get("APP_PORT")


if __name__ == "__main__":
    print(SECRET)
