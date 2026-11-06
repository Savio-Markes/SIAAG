
# Desenvolvido por: Fábio Barbosa

from app.auth import permission_service


def test_listar_permissoes_usuario(monkeypatch):
    permissoes = ["animais.visualizar", "estoque.visualizar"]

    monkeypatch.setattr(
        permission_service,
        "buscar_codigos_por_usuario",
        lambda usuario_id: permissoes
    )

    resultado = permission_service.listar_permissoes_usuario(1)

    assert resultado == permissoes


def test_listar_permissoes_sem_usuario():
    assert permission_service.listar_permissoes_usuario(None) == []


def test_verificar_permissao_usuario(monkeypatch):
    monkeypatch.setattr(
        permission_service,
        "usuario_possui_permissao",
        lambda usuario_id, codigo: True
    )

    resultado = permission_service.verificar_permissao_usuario(
        1, "animais.visualizar"
    )

    assert resultado is True


def test_verificar_permissao_inexistente(monkeypatch):
    monkeypatch.setattr(
        permission_service,
        "usuario_possui_permissao",
        lambda usuario_id, codigo: False
    )

    resultado = permission_service.verificar_permissao_usuario(
        1, "animais.editar"
    )

    assert resultado is False


def test_verificar_permissao_sem_usuario():
    assert permission_service.verificar_permissao_usuario(
        None, "animais.visualizar"
    ) is False


def test_conceder_permissao_usuario(monkeypatch):
    monkeypatch.setattr(
        permission_service,
        "conceder_permissao",
        lambda usuario_id, codigo, concedido_por: True
    )

    resultado = permission_service.conceder_permissao_usuario(
        2, "animais.visualizar", 1
    )

    assert resultado is True


def test_conceder_permissao_sem_dados():
    resultado = permission_service.conceder_permissao_usuario(
        None, "animais.visualizar", 1
    )

    assert resultado is False


def test_revogar_permissao_usuario(monkeypatch):
    monkeypatch.setattr(
        permission_service,
        "revogar_permissao",
        lambda usuario_id, codigo, revogado_por: True
    )

    resultado = permission_service.revogar_permissao_usuario(
        2, "animais.visualizar", 1
    )

    assert resultado is True


def test_revogar_permissao_sem_dados():
    resultado = permission_service.revogar_permissao_usuario(
        2, "", 1
    )

    assert resultado is False
