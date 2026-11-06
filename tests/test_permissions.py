# Desenvolvido por: Fábio Barbosa

from app import create_app
from app.permissions import permission_required


def criar_cliente():
    """Prepara a aplicação e uma rota protegida para os testes."""

    app = create_app()
    app.config["TESTING"] = True

    rota_protegida = permission_required(
        "animais.visualizar"
    )(lambda: "Acesso permitido")

    app.add_url_rule(
        "/teste-permissao",
        "teste_permissao",
        rota_protegida
    )

    return app.test_client()


def test_usuario_sem_login_e_redirecionado():
    """Verifica o bloqueio de usuários não autenticados."""

    cliente = criar_cliente()

    resposta = cliente.get("/teste-permissao")

    assert resposta.status_code == 302
    assert "/login" in resposta.headers["Location"]


def test_usuario_sem_permissao_recebe_403():
    """Verifica o bloqueio de usuário sem a permissão exigida."""

    cliente = criar_cliente()

    with cliente.session_transaction() as sessao:
        sessao["usuario_id"] = 1
        sessao["permissoes"] = []

    resposta = cliente.get("/teste-permissao")

    assert resposta.status_code == 403


def test_usuario_com_permissao_acessa_rota():
    """Verifica o acesso de usuário com a permissão exigida."""

    cliente = criar_cliente()

    with cliente.session_transaction() as sessao:
        sessao["usuario_id"] = 1
        sessao["permissoes"] = ["animais.visualizar"]

    resposta = cliente.get("/teste-permissao")

    assert resposta.status_code == 200
    assert resposta.data == b"Acesso permitido"