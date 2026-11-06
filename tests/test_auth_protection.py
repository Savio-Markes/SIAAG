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