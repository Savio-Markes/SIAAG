
from app import create_app
from app.extensions import get_db
from werkzeug.security import generate_password_hash
from getpass import getpass

app = create_app()

with app.app_context():
    senha = getpass("Digite a senha do usuário de teste: ")

    if len(senha) < 8:
        raise ValueError("A senha deve ter pelo menos 8 caracteres.")

    senha_hash = generate_password_hash(senha)

    conexao = get_db()

    try:
        with conexao.cursor() as cursor:
            cursor.execute(
                "SELECT id FROM usuarios WHERE login = %s",
                ("teste.siaag",)
            )

            if cursor.fetchone():
                print("Esse usuário já existe.")
            else:
                cursor.execute("""
                    INSERT INTO usuarios
                    (nome, login, senha_hash, funcao_referencia,
                     ativo, criado_em)
                    VALUES (%s, %s, %s, %s, %s, NOW())
                """, (
                    "Usuário de Teste",
                    "teste.siaag",
                    senha_hash,
                    "Administrador",
                    1
                ))

                conexao.commit()
                print("Usuário de teste criado com sucesso!")

    except Exception:
        conexao.rollback()
        raise
