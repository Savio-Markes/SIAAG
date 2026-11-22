
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

    # O estado de atividade é controlado apenas pelas ações específicas.
    if "ativo" in dados:
        raise AnimalServiceError(
            "O estado de atividade deve ser alterado pela ação de "
            "inativar ou reativar."
        )

    campos_obrigatorios = ("identificacao", "especie", "situacao")

    if not atualizacao:
        for campo in campos_obrigatorios:
            if not dados.get(campo) or not str(dados[campo]).strip():
                raise AnimalServiceError(
                    f"O campo {campo} é obrigatório."
                )

    campos_texto = (
        "identificacao", "nome", "especie", "raca", "sexo",
        "origem", "localizacao", "situacao", "observacoes"
    )

    for campo in campos_texto:
        if campo in dados and dados[campo] is not None:
            dados[campo] = str(dados[campo]).strip() or None

    if atualizacao and "identificacao" in dados:
        if not dados["identificacao"]:
            raise AnimalServiceError(
                "O campo identificacao não pode ser vazio."
            )

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

    return dados


def validar_identificacao_unica(identificacao, animal_id=None):
    """Verifica se a identificação já pertence a outro animal."""

    animal_existente = (
        animal_repository.buscar_animal_por_identificacao(
            identificacao
        )
    )

    if animal_existente:
        if animal_id is None or animal_existente["id"] != animal_id:
            raise AnimalServiceError(
                "Já existe um animal cadastrado com essa identificação."
            )


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


def contar_animais(filtros=None):
    """Conta os animais considerando os filtros aplicados."""

    return animal_repository.contar_animais(filtros)


def buscar_animal(animal_id):
    """Busca um animal pelo ID."""

    animal = animal_repository.buscar_animal_por_id(animal_id)

    if not animal:
        raise AnimalServiceError("Animal não encontrado.")

    return animal


def cadastrar_animal(dados, criado_por):
    """Valida e cadastra um novo animal."""

    dados = validar_dados_animal(dados)
    validar_identificacao_unica(dados["identificacao"])

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

    if "identificacao" in dados:
        validar_identificacao_unica(
            dados["identificacao"],
            animal_id=animal_id
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


def reativar_animal(animal_id):
    """Reativa um animal anteriormente inativado."""

    animal = buscar_animal(animal_id)

    if int(animal["ativo"]) == 1:
        raise AnimalServiceError("O animal já está ativo.")

    reativado = animal_repository.reativar_animal(animal_id)

    if not reativado:
        raise AnimalServiceError(
            "Não foi possível reativar o animal."
        )

    return True


def excluir_animal(animal_id, excluido_por):
    """
    Solicita a exclusão definitiva ao repositório.

    A exclusão só é permitida quando não existem registros
    históricos vinculados ao animal.
    """

    resultado = animal_repository.excluir_animal(
        animal_id=animal_id,
        excluido_por=excluido_por
    )

    status = resultado.get("status")

    if status == "nao_encontrado":
        raise AnimalServiceError("Animal não encontrado.")

    if status == "possui_historico":
        nomes = {
            "pesagens": "pesagem(ns)",
            "atendimentos": "atendimento(s) veterinário(s)",
            "ocorrencias": "ocorrência(s)",
            "atividades": "atividade(s)"
        }

        vinculos = resultado.get("vinculos", {})

        detalhes = [
            f"{total} {nomes.get(tipo, tipo)}"
            for tipo, total in vinculos.items()
        ]

        mensagem = (
            "A exclusão não pode ser realizada. "
            "O animal possui histórico vinculado: "
            + ", ".join(detalhes)
            + ". O cadastro deve ser preservado."
        )

        raise AnimalServiceError(mensagem)

    if status != "excluido":
        raise AnimalServiceError(
            "Não foi possível concluir a exclusão do animal."
        )

    return True


def obter_indicadores():
    """Retorna indicadores gerais do módulo de animais."""

    total = animal_repository.contar_animais()
    ativos = animal_repository.contar_animais_ativos()
    especies = animal_repository.contar_animais_por_especie()
    situacoes = animal_repository.contar_animais_por_situacao()

    return {
        "total": total,
        "ativos": ativos,
        "inativos": total - ativos,
        "especies": especies,
        "situacoes": situacoes
    }