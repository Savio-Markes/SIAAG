
from flask import Flask
from config import Config
from app.database import close_db


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    app.teardown_appcontext(close_db)

    # Registro dos módulos
    from app.auth.routes import auth_bp
    @app.route("/")
    def inicio():
        return "SIAAG — Servidor funcionando!"

    # app.register_blueprint(auth_bp)
    # Registre os demais módulos aqui quando necessário.

    return app
