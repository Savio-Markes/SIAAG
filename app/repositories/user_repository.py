# Desenvolvido por: Fábio Barbosa

from app.extensions import get_db


# Acesso aos dados dos usuários no banco MySQL.

def buscar_por_login(login):
    """Busca um usuário pelo seu login."""

    conexao = get_db()

    with conexao.cursor() as cursor:
        cursor.execute(
            """
            SELECT id, nome, login, senha_hash, ativo
            FROM usuarios
            WHERE login = %s
            LIMIT 1
            """,
            (login,)
        )

        return cursor.fetchone()