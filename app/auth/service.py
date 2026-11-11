# Desenvolvido por: Fábio Barbosa

from werkzeug.security import check_password_hash
from app.repositories.user_repository import buscar_por_login


# Serviços e regras de negócio da autenticação.

def validar_credenciais(usuario, senha):
    """Verifica se os campos obrigatórios foram preenchidos."""

    return bool(usuario and senha)


def verificar_senha(senha_digitada, senha_hash):
    """Compara a senha informada com o hash armazenado."""

    return check_password_hash(senha_hash, senha_digitada)


def autenticar_usuario(login, senha):
    """Autentica o usuário e verifica se sua conta está ativa."""

    if not validar_credenciais(login, senha):
        return None

    usuario = buscar_por_login(login)

    if not usuario or not usuario["ativo"]:
        return None

    if not verificar_senha(senha, usuario["senha_hash"]):
        return None

    return usuario