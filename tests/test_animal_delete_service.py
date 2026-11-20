
# Desenvolvido por: Fábio Barbosa

import pytest

from app.animals import service as animal_service


def test_excluir_animal_sem_historico(monkeypatch):
    """Permite exclusão quando não existem vínculos históricos."""

    chamada = {}

    def excluir(animal_id, excluido_por):
        chamada["animal_id"] = animal_id
        chamada["excluido_por"] = excluido_por
        return {"status": "excluido"}

    monkeypatch.setattr(
        animal_service.animal_repository,
        "excluir_animal",
        excluir
    )

    resultado = animal_service.excluir_animal(10, 1)

    assert resultado is True
    assert chamada == {
        "animal_id": 10,
        "excluido_por": 1
    }


def test_bloquear_exclusao_com_historico(monkeypatch):
    """Bloqueia a exclusão quando existem registros vinculados."""

    monkeypatch.setattr(
        animal_service.animal_repository,
        "excluir_animal",
        lambda animal_id, excluido_por: {
            "status": "possui_historico",
            "vinculos": {
                "pesagens": 2,
                "atendimentos": 1
            }
        }
    )

    with pytest.raises(
        animal_service.AnimalServiceError,
        match="histórico vinculado"
    ):
        animal_service.excluir_animal(10, 1)


def test_excluir_animal_inexistente(monkeypatch):
    """Retorna erro quando o animal não existe."""

    monkeypatch.setattr(
        animal_service.animal_repository,
        "excluir_animal",
        lambda animal_id, excluido_por: {
            "status": "nao_encontrado"
        }
    )

    with pytest.raises(
        animal_service.AnimalServiceError,
        match="Animal não encontrado"
    ):
        animal_service.excluir_animal(999, 1)


def test_excluir_animal_rejeita_status_desconhecido(monkeypatch):
    """Não considera sucesso um retorno inesperado do repositório."""

    monkeypatch.setattr(
        animal_service.animal_repository,
        "excluir_animal",
        lambda animal_id, excluido_por: {
            "status": "erro"
        }
    )

    with pytest.raises(
        animal_service.AnimalServiceError,
        match="Não foi possível concluir"
    ):
        animal_service.excluir_animal(10, 1)
