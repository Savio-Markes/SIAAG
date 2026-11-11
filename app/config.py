
import os


class Config:
    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "chave-desenvolvimento-siaag"
    )

    MYSQL_HOST = "localhost"
    MYSQL_PORT = 3306
    MYSQL_USER = "root"
    MYSQL_PASSWORD = "12345678"
    MYSQL_DATABASE = "SIAAG"

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"