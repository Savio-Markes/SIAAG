
from flask import Flask

from config import Config
from app.extensions import close_db


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    app.teardown_appcontext(close_db)

    return app
