
# Sávio — 06/11/2026

import os
from sqlalchemy import URL


class Config:
    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "chave-desenvolvimento-siaag"
    )

    MYSQL_HOST = os.environ.get("MYSQL_HOST", "localhost")
    MYSQL_PORT = int(os.environ.get("MYSQL_PORT", "3306"))
    MYSQL_USER = os.environ.get("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "")
    MYSQL_DATABASE = os.environ.get("MYSQL_DATABASE", "siaag")

    SQLALCHEMY_DATABASE_URI = URL.create(
        "mysql+pymysql",
        username="root",
        password="12345678",
        host="localhost",
        port="3306",
        database="SIAAG",
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"