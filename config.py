# Desenvolvido por: Fábio Barbosa

import os

from dotenv import load_dotenv

load_dotenv()


class Config:

    MYSQL_HOST = os.environ.get("MYSQL_HOST", "localhost")
    MYSQL_PORT = int(os.environ.get("MYSQL_PORT", "3306"))
    MYSQL_USER = os.environ.get("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "12345678")
    MYSQL_DATABASE = os.environ.get("MYSQL_DATABASE", "siaag")

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"