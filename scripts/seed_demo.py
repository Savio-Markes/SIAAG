
import sys
from pathlib import Path
from getpass import getpass

# Localiza a raiz do projeto SIAAG
RAIZ_PROJETO = Path(__file__).resolve().parent.parent

# Permite importar os módulos da aplicação
sys.path.insert(0, str(RAIZ_PROJETO))

from app import create_app
from app.extensions import get_db
from werkzeug.security import generate_password_hash


def criar_usuario_temporario():
    app = create_app()

    with app.app_context():
        nome = "Usuário Temporário"
        login = "teste.siaag"
        funcao = "Servidor"

        senha = getpass("Digite a senha temporária: ")

        if len(senha) < 8:
            print("Erro: a senha deve ter pelo menos 8 caracteres.")
            return

        db = get_db()

        try:
            with db.cursor() as cursor:
                # Verifica se o login já existe
                cursor.execute(
                    "SELECT id FROM usuarios WHERE login = %s",
                    (login,)
                )

                if cursor.fetchone():
                    print(f"O login '{login}' já está cadastrado.")
                    return

                # Cria o usuário com senha criptografada
                cursor.execute(
                    """
                    INSERT INTO usuarios
                    (nome, login, senha_hash, funcao_referencia, ativo)
                    VALUES (%s, %s, %s, %s, 1)
                    """,
                    (
                        nome,
                        login,
                        generate_password_hash(senha),
                        funcao
                    )
                )

            db.commit()

            print("\nUsuário temporário criado com sucesso!")
            print(f"Login: {login}")
            print("Senha: a que você informou anteriormente.")

        except Exception as erro:
            db.rollback()
            print(f"Erro ao criar usuário: {erro}")


if __name__ == "__main__":
    criar_usuario_temporario()
