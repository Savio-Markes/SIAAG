
# Desenvolvido por: Fábio Barbosa

from app.repositories.user_repository import listar_usuarios as buscar_usuarios


def listar_usuarios():
    """Obtém a lista de usuários cadastrados."""

    return buscar_usuarios()
