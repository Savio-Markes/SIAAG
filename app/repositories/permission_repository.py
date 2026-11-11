
# Desenvolvido por: Fábio Barbosa

from app.extensions import get_db


# Acesso aos dados de permissões no banco MySQL.


def buscar_codigos_por_usuario(usuario_id):
    """Retorna os códigos de permissões concedidos a um usuário."""

    conexao = get_db()

    with conexao.cursor() as cursor:
        cursor.execute(
            """
            SELECT p.codigo
            FROM usuario_permissoes AS up
            INNER JOIN permissoes AS p
                ON p.id = up.permissao_id
            WHERE up.usuario_id = %s
            """,
            (usuario_id,)
        )

        resultados = cursor.fetchall()

    return [registro["codigo"] for registro in resultados]


def usuario_possui_permissao(usuario_id, codigo):
    """Verifica se um usuário possui determinada permissão."""

    conexao = get_db()

    with conexao.cursor() as cursor:
        cursor.execute(
            """
            SELECT 1
            FROM usuario_permissoes AS up
            INNER JOIN permissoes AS p
                ON p.id = up.permissao_id
            WHERE up.usuario_id = %s
              AND p.codigo = %s
            LIMIT 1
            """,
            (usuario_id, codigo)
        )

        return cursor.fetchone() is not None


def conceder_permissao(usuario_id, codigo, concedido_por):
    """Concede uma permissão a um usuário e registra a auditoria."""

    conexao = get_db()

    try:
        with conexao.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, modulo
                FROM permissoes
                WHERE codigo = %s
                LIMIT 1
                """,
                (codigo,)
            )

            permissao = cursor.fetchone()

            if not permissao:
                return False

            cursor.execute(
                """
                SELECT 1
                FROM usuario_permissoes
                WHERE usuario_id = %s
                  AND permissao_id = %s
                LIMIT 1
                """,
                (usuario_id, permissao["id"])
            )

            if cursor.fetchone():
                return False

            cursor.execute(
                """
                INSERT INTO usuario_permissoes
                    (usuario_id, permissao_id, concedido_por)
                VALUES (%s, %s, %s)
                """,
                (usuario_id, permissao["id"], concedido_por)
            )

            cursor.execute(
                """
                INSERT INTO logs_auditoria
                    (usuario_id, data_hora, modulo, acao,
                     entidade, registro_id, resultado, detalhes_resumidos)
                VALUES (%s, NOW(), %s, 'conceder_permissao',
                        'usuario_permissoes', %s, 'sucesso', %s)
                """,
                (
                    concedido_por,
                    permissao["modulo"],
                    usuario_id,
                    f"Permissão {codigo} concedida ao usuário {usuario_id}."
                )
            )

        conexao.commit()
        return True

    except Exception:
        conexao.rollback()
        raise


def revogar_permissao(usuario_id, codigo, revogado_por):
    """Revoga uma permissão e registra a auditoria."""

    conexao = get_db()

    try:
        with conexao.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, modulo
                FROM permissoes
                WHERE codigo = %s
                LIMIT 1
                """,
                (codigo,)
            )

            permissao = cursor.fetchone()

            if not permissao:
                return False

            cursor.execute(
                """
                DELETE FROM usuario_permissoes
                WHERE usuario_id = %s
                  AND permissao_id = %s
                """,
                (usuario_id, permissao["id"])
            )

            if cursor.rowcount == 0:
                return False

            cursor.execute(
                """
                INSERT INTO logs_auditoria
                    (usuario_id, data_hora, modulo, acao,
                     entidade, registro_id, resultado, detalhes_resumidos)
                VALUES (%s, NOW(), %s, 'revogar_permissao',
                        'usuario_permissoes', %s, 'sucesso', %s)
                """,
                (
                    revogado_por,
                    permissao["modulo"],
                    usuario_id,
                    f"Permissão {codigo} revogada do usuário {usuario_id}."
                )
            )

        conexao.commit()
        return True

    except Exception:
        conexao.rollback()
        raise
