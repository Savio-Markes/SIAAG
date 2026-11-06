# Desenvolvido por: Fábio Barbosa

from app import create_app


def test_dashboard_bloqueia_usuario_sem_login():
    """Verifica se usuários sem sessão são redirecionados ao login."""

    app = create_app()
    app.config["TESTING"] = True

    cliente = app.test_client()

    resposta = cliente.get("/")

    assert resposta.status_code == 302
    assert "/login" in resposta.headers["Location"]


def test_dashboard_permite_usuario_autenticado():
    """Verifica se usuários autenticados conseguem acessar o Dashboard."""

    app = create_app()
    app.config["TESTING"] = True

    cliente = app.test_client()

    with cliente.session_transaction() as sessao:
        sessao["usuario_id"] = 1
        sessao["usuario_nome"] = "Usuário de teste"

    resposta = cliente.get("/")

    assert resposta.status_code == 200


def test_logout_encerra_sessao():
    """Verifica se o logout encerra a sessão do usuário."""

    app = create_app()
    app.config["TESTING"] = True

    cliente = app.test_client()

    # Simula um usuário autenticado
    with cliente.session_transaction() as sessao:
        sessao["usuario_id"] = 1
        sessao["usuario_nome"] = "Usuário de teste"

    # Executa o logout
    resposta = cliente.post("/logout")

    assert resposta.status_code == 302
    assert "/login" in resposta.headers["Location"]

    # Confirma que a sessão foi encerrada
    with cliente.session_transaction() as sessao:
        assert "usuario_id" not in sessao