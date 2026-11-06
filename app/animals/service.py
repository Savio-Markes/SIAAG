# Desenvolvido por: Fábio Barbosa

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
        identificacao = dados.get("identificacao")
        especie = dados.get("especie")
        situacao = dados.get("situacao")

        if not identificacao or not str(identificacao).strip():
            raise AnimalServiceError("A identificação é obrigatória.")

        if not especie or not str(especie).strip():
            raise AnimalServiceError("A espécie é obrigatória.")

        if not situacao or not str(situacao).strip():
            raise AnimalServiceError("A situação é obrigatória.")

    campos_texto = (
        "identificacao",
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
                str(dados["nascimento"]),
                "%Y-%m-%d"
            ).date()
        except ValueError:
            raise AnimalServiceError(
                "A data de nascimento é inválida."
            )

        if nascimento > date.today():
            raise AnimalServiceError(
                "A data de nascimento não pode ser futura."
            )

    for campo in ("data_entrada",):
        if campo in dados and dados[campo]:
            try:
                datetime.strptime(str(dados[campo]), "%Y-%m-%d")
            except ValueError:
                raise AnimalServiceError(
                    f"A data de {campo.replace('_', ' ')} é inválida."
                )

    if "ativo" in dados and dados["ativo"] not in (0, 1, False, True):
        raise AnimalServiceError("O estado de atividade é inválido.")

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

    existente = animal_repository.buscar_animal_por_identificacao(
        dados["identificacao"]
    )

    if existente:
        raise AnimalServiceError(
            "Já existe um animal com essa identificação."
        )

    return animal_repository.criar_animal(
        dados=dados,
        criado_por=criado_por
    )


def editar_animal(animal_id, dados):
    """Valida e atualiza os dados de um animal."""

    buscar_animal(animal_id)

    dados = validar_dados_animal(
        dados,
        atualizacao=True
    )

    if "identificacao" in dados and dados["identificacao"]:
        existente = animal_repository.buscar_animal_por_identificacao(
            dados["identificacao"]
        )

        if existente and existente["id"] != animal_id:
            raise AnimalServiceError(
                "Essa identificação já pertence a outro animal."
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