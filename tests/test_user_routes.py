
# Desenvolvido por: Fábio Barbosa

from app import create_app
from app import permissions
from app.users import routes as users_routes


def preparar_cliente(monkeypatch, autorizado=True):
    """Prepara o cliente com usuário autenticado."""

    app = create_app()
    app.config["TESTING"] = True

    monkeypatch.setattr(
        permissions,
        "verificar_permissao_usuario",
        lambda usuario_id, codigo: autorizado
    )

    cliente = app.test_client()

    with cliente.session_transaction() as sessao:
        sessao["usuario_id"] = 1
        sessao["usuario_nome"] = "Coordenador"

    return cliente


def test_consultar_permissoes_usuario(monkeypatch):
    monkeypatch.setattr(
        users_routes,
        "listar_permissoes_usuario",
        lambda usuario_id: ["animais.visualizar"]
    )

    cliente = preparar_cliente(monkeypatch)
    resposta = cliente.get("/usuarios/2/permissoes")

    assert resposta.status_code == 200
    assert resposta.json["permissoes"] == ["animais.visualizar"]


def test_conceder_permissao(monkeypatch):
    monkeypatch.setattr(
        users_routes,
        "conceder_permissao_usuario",
        lambda usuario_id, codigo, concedido_por: True
    )

    cliente = preparar_cliente(monkeypatch)

    resposta = cliente.post(
        "/usuarios/2/permissoes",
        json={"codigo": "animais.visualizar"}
    )

    assert resposta.status_code == 201


def test_revogar_permissao(monkeypatch):
    monkeypatch.setattr(
        users_routes,
        "revogar_permissao_usuario",
        lambda usuario_id, codigo, revogado_por: True
    )

    cliente = preparar_cliente(monkeypatch)

    resposta = cliente.delete(
        "/usuarios/2/permissoes/animais.visualizar"
    )

    assert resposta.status_code == 200


def test_bloquear_usuario_sem_permissao(monkeypatch):
    cliente = preparar_cliente(monkeypatch, autorizado=False)

    resposta = cliente.get("/usuarios/2/permissoes")

    assert resposta.status_code == 403


def test_concessao_sem_codigo(monkeypatch):
    cliente = preparar_cliente(monkeypatch)

    resposta = cliente.post(
        "/usuarios/2/permissoes",
        json={}
    )

    assert resposta.status_code == 400
