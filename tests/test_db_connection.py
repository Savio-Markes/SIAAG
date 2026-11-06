# Desenvolvido por: Fábio Barbosa

from app import create_app
from app.extensions import get_db


def test_conexao_mysql():
    """Verifica se a aplicação consegue acessar o MySQL."""

    app = create_app()

    with app.app_context():
        conexao = get_db()

        with conexao.cursor() as cursor:
            cursor.execute("SELECT 1 AS teste")
            resultado = cursor.fetchone()

        assert resultado["teste"] == 1