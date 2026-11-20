
# Desenvolvido por: Fábio Barbosa

from app import create_app
from app.extensions import get_db


def test_conexao_mysql():
    """Verifica a conexão e a estrutura do banco de dados."""

    app = create_app()

    with app.app_context():
        conexao = get_db()

        with conexao.cursor() as cursor:
            cursor.execute("SELECT 1 AS teste")
            resultado = cursor.fetchone()

            assert resultado["teste"] == 1

            cursor.execute("SELECT DATABASE() AS banco")
            banco = cursor.fetchone()

            assert banco["banco"] == "siaag"

            cursor.execute("SHOW TABLES")
            tabelas = cursor.fetchall()

            assert len(tabelas) == 22

            print("\nCONEXÃO COM SUCESSO!")
            print("Banco:", banco["banco"])
            print("Tabelas encontradas:", len(tabelas))


if __name__ == "__main__":
    test_conexao_mysql()
