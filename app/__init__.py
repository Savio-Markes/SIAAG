
# Desenvolvido por: Fábio Barbosa

from flask import Flask

from config import Config
from app.extensions import close_db


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    app.teardown_appcontext(close_db)

    # Registro dos módulos
    from app.auth.routes import auth_bp
    from app.dashboard.routes import dashboard_bp
    from app.users.routes import users_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(users_bp)

    return app
