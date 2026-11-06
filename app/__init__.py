from flask import Flask
from config import Config
from app.extensions import db, migrate, close_db


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    app.teardown_appcontext(close_db)

    # Registro dos módulos
    from app.auth.routes import auth_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)

    return app