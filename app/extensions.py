# Desenvolvido por: Fábio Barbosa

import pymysql
from flask import current_app, g


def get_db():
    """Obtém ou cria a conexão com o banco MySQL."""

    if "db" not in g:
        g.db = pymysql.connect(
            host=current_app.config["MYSQL_HOST"],
            port=current_app.config["MYSQL_PORT"],
            user=current_app.config["MYSQL_USER"],
            password=current_app.config["MYSQL_PASSWORD"],
            database=current_app.config["MYSQL_DATABASE"],
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor
        )

    return g.db


def close_db(error=None):
    """Encerra a conexão com o banco ao finalizar a requisição."""

    connection = g.pop("db", None)

    if connection is not None and connection.open:
        connection.close()