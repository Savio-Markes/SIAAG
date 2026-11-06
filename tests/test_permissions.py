
# Desenvolvido por: Fábio Barbosa

from app import create_app
from app import permissions


def criar_cliente(monkeypatch, permissao_concedida=False):
    """Prepara uma rota protegida para os testes."""

    app = create_app()
    app.config["TESTING"] = True

    monkeypatch.setattr(
        permissions,
        "verificar_permissao_usuario",
        lambda usuario_id, codigo: permissao_concedida
    )

    rota_protegida = permissions.permission_required(
        "animais.visualizar"
    )(lambda: "Acesso permitido")

    app.add_url_rule(
        "/teste-permissao",
        "teste_permissao",
        rota_protegida
    )

    return app.test_client()


def test_usuario_sem_login_e_redirecionado(monkeypatch):
    """Verifica o bloqueio de usuários não autenticados."""

    cliente = criar_cliente(monkeypatch)

    resposta = cliente.get("/teste-permissao")

    assert resposta.status_code == 302
    assert "/login" in resposta.headers["Location"]


def test_usuario_sem_permissao_recebe_403(monkeypatch):
    """Verifica o bloqueio de usuário sem autorização."""

    cliente = criar_cliente(monkeypatch)

    with cliente.session_transaction() as sessao:
        sessao["usuario_id"] = 1

    resposta = cliente.get("/teste-permissao")

    assert resposta.status_code == 403


def test_usuario_com_permissao_acessa_rota(monkeypatch):
    """Verifica o acesso de usuário autorizado."""

    cliente = criar_cliente(monkeypatch, True)

    with cliente.session_transaction() as sessao:
        sessao["usuario_id"] = 1

    resposta = cliente.get("/teste-permissao")

    assert resposta.status_code == 200
    assert resposta.data == b"Acesso permitido"


def test_permissao_invalida_e_bloqueada(monkeypatch):
    """Verifica o bloqueio de códigos não cadastrados."""

    cliente = criar_cliente(monkeypatch, True)

    with cliente.session_transaction() as sessao:
        sessao["usuario_id"] = 1

    resposta = cliente.get("/teste-permissao")

    assert resposta.status_code == 200
