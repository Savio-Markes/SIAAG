
# Desenvolvido por: Fábio Barbosa

from app.repositories.permission_repository import (
    buscar_codigos_por_usuario,
    usuario_possui_permissao,
    conceder_permissao,
    revogar_permissao
)


# Regras de negócio relacionadas às permissões.


def listar_permissoes_usuario(usuario_id):
    """Lista todas as permissões concedidas a um usuário."""

    if not usuario_id:
        return []

    return buscar_codigos_por_usuario(usuario_id)


def verificar_permissao_usuario(usuario_id, codigo):
    """Verifica se o usuário possui uma permissão específica."""

    if not usuario_id or not codigo:
        return False

    return usuario_possui_permissao(usuario_id, codigo)


def conceder_permissao_usuario(usuario_id, codigo, concedido_por):
    """Valida e solicita a concessão de uma permissão."""

    if not usuario_id or not codigo or not concedido_por:
        return False

    return conceder_permissao(
        usuario_id,
        codigo,
        concedido_por
    )


def revogar_permissao_usuario(usuario_id, codigo, revogado_por):
    """Valida e solicita a revogação de uma permissão."""

    if not usuario_id or not codigo or not revogado_por:
        return False

    return revogar_permissao(
        usuario_id,
        codigo,
        revogado_por
    )
