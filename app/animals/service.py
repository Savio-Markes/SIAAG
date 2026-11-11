
from datetime import date, datetime

from app.repositories import animal_repository


class AnimalServiceError(Exception):
    """Erro relacionado às regras de negócio dos animais."""
    pass


def validar_dados_animal(dados, atualizacao=False):
    """Valida os dados recebidos para cadastro ou edição."""

    if not isinstance(dados, dict):
        raise AnimalServiceError("Dados do animal inválidos.")

    if not atualizacao:
        for campo in ("nome", "especie", "situacao"):
            if not dados.get(campo) or not str(dados[campo]).strip():
                raise AnimalServiceError(
                    f"O campo {campo} é obrigatório."
                )

    campos_texto = (
        "nome",
        "especie",
        "raca",
        "sexo",
        "origem",
        "localizacao",
        "situacao",
        "observacoes"
    )

    for campo in campos_texto:
        if campo in dados and isinstance(dados[campo], str):
            dados[campo] = dados[campo].strip() or None

    if "nascimento" in dados and dados["nascimento"]:
        try:
            nascimento = datetime.strptime(
                str(dados["nascimento"]), "%Y-%m-%d"
            ).date()
        except ValueError:
            raise AnimalServiceError(
                "A data de nascimento é inválida."
            )

        if nascimento > date.today():
            raise AnimalServiceError(
                "A data de nascimento não pode ser futura."
            )

    if "data_entrada" in dados and dados["data_entrada"]:
        try:
            datetime.strptime(
                str(dados["data_entrada"]), "%Y-%m-%d"
            )
        except ValueError:
            raise AnimalServiceError(
                "A data de entrada é inválida."
            )

    if "ativo" in dados and dados["ativo"] not in (
        0, 1, False, True
    ):
        raise AnimalServiceError(
            "O estado de atividade é inválido."
        )

    return dados


def listar_animais(filtros=None, limite=50, deslocamento=0):
    """Lista animais com filtros e paginação."""

    if not isinstance(limite, int) or limite < 1 or limite > 100:
        raise AnimalServiceError("Limite de consulta inválido.")

    if not isinstance(deslocamento, int) or deslocamento < 0:
        raise AnimalServiceError("Deslocamento inválido.")

    return animal_repository.listar_animais(
        filtros=filtros,
        limite=limite,
        deslocamento=deslocamento
    )


def buscar_animal(animal_id):
    """Busca um animal pelo ID."""

    animal = animal_repository.buscar_animal_por_id(animal_id)

    if not animal:
        raise AnimalServiceError("Animal não encontrado.")

    return animal


def cadastrar_animal(dados, criado_por):
    """Valida e cadastra um novo animal."""

    dados = validar_dados_animal(dados)

    return animal_repository.criar_animal(
        dados=dados,
        criado_por=criado_por
    )


def editar_animal(animal_id, dados):
    """Valida e atualiza os dados cadastrais."""

    buscar_animal(animal_id)

    dados = validar_dados_animal(
        dados,
        atualizacao=True
    )

    atualizado = animal_repository.atualizar_animal(
        animal_id,
        dados
    )

    if not atualizado:
        raise AnimalServiceError(
            "Não foi possível atualizar o animal."
        )

    return True


def inativar_animal(animal_id):
    """Inativa um animal sem excluir seu histórico."""

    buscar_animal(animal_id)

    inativado = animal_repository.inativar_animal(animal_id)

    if not inativado:
        raise AnimalServiceError(
            "Não foi possível inativar o animal."
        )

    return True
