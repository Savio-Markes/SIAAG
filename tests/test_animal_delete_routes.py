
# Desenvolvido por: Fábio Barbosa

from app import create_app, permissions
from app.animals import service as animal_service


def preparar_cliente(monkeypatch, autorizado=True):
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

    return cliente


def test_rota_excluir_animal_com_sucesso(monkeypatch):
    monkeypatch.setattr(
        animal_service,
        "excluir_animal",
        lambda animal_id, excluido_por: True
    )

    cliente = preparar_cliente(monkeypatch)
    resposta = cliente.post("/animais/10/excluir")

    assert resposta.status_code == 200
    assert resposta.json["sucesso"] is True


def test_rota_excluir_animal_com_historico(monkeypatch):
    def excluir(animal_id, excluido_por):
        raise animal_service.AnimalServiceError(
            "A exclusão não pode ser realizada. "
            "O animal possui histórico vinculado: 2 pesagem(ns)."
        )

    monkeypatch.setattr(
        animal_service,
        "excluir_animal",
        excluir
    )

    cliente = preparar_cliente(monkeypatch)
    resposta = cliente.post("/animais/10/excluir")

    assert resposta.status_code == 409
    assert resposta.json["sucesso"] is False


def test_rota_excluir_animal_inexistente(monkeypatch):
    def excluir(animal_id, excluido_por):
        raise animal_service.AnimalServiceError(
            "Animal não encontrado."
        )

    monkeypatch.setattr(
        animal_service,
        "excluir_animal",
        excluir
    )

    cliente = preparar_cliente(monkeypatch)
    resposta = cliente.post("/animais/999/excluir")

    assert resposta.status_code == 404


def test_rota_excluir_animal_sem_permissao(monkeypatch):
    cliente = preparar_cliente(monkeypatch, autorizado=False)

    resposta = cliente.post("/animais/10/excluir")

    assert resposta.status_code == 403
