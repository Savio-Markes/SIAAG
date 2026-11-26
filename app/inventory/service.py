# Desenvolvido por: Fábio Barbosa

from datetime import date, datetime
from decimal import Decimal, InvalidOperation

from app.repositories import inventory_repository


class InventoryServiceError(Exception):
    """Erro relacionado às regras de negócio do estoque."""
    pass


# ============================================================
# TRATAMENTO DE ERROS
# ============================================================

def _tratar_erro_repositorio(erro):
    if isinstance(erro, InventoryServiceError):
        raise erro

    if isinstance(
        erro,
        inventory_repository.InventoryRepositoryError
    ):
        raise InventoryServiceError(str(erro))

    if isinstance(erro, ValueError):
        raise InventoryServiceError(str(erro))

    raise InventoryServiceError(
        "Não foi possível concluir a operação no estoque."
    )


# ============================================================
# VALIDAÇÕES GERAIS
# ============================================================

def _converter_decimal(valor, campo):
    try:
        numero = Decimal(str(valor).replace(",", "."))
    except (InvalidOperation, TypeError, ValueError):
        raise InventoryServiceError(
            f"O campo {campo} deve conter um número válido."
        )

    if not numero.is_finite():
        raise InventoryServiceError(
            f"O campo {campo} deve conter um número válido."
        )

    return numero


def _validar_quantidade(valor):
    quantidade = _converter_decimal(valor, "quantidade")

    if quantidade <= 0:
        raise InventoryServiceError(
            "A quantidade deve ser maior que zero."
        )

    return quantidade


def _validar_id(valor, campo):
    try:
        identificador = int(valor)
    except (TypeError, ValueError):
        raise InventoryServiceError(
            f"O campo {campo} é inválido."
        )

    if identificador <= 0:
        raise InventoryServiceError(
            f"O campo {campo} é inválido."
        )

    return identificador


def _validar_texto(valor, campo, obrigatorio=False):
    if valor is None:
        if obrigatorio:
            raise InventoryServiceError(
                f"O campo {campo} é obrigatório."
            )
        return None

    texto = str(valor).strip()

    if obrigatorio and not texto:
        raise InventoryServiceError(
            f"O campo {campo} é obrigatório."
        )

    return texto or None


# ============================================================
# CATEGORIAS
# ============================================================

def listar_categorias(apenas_ativas=True):
    return inventory_repository.listar_categorias(
        apenas_ativas=apenas_ativas
    )


def validar_categoria(categoria_id):
    if categoria_id in (None, ""):
        return None

    categoria_id = _validar_id(
        categoria_id,
        "categoria"
    )

    categoria = inventory_repository.buscar_categoria_por_id(
        categoria_id
    )

    if not categoria:
        raise InventoryServiceError(
            "A categoria informada não existe."
        )

    if int(categoria["ativa"]) != 1:
        raise InventoryServiceError(
            "A categoria selecionada está inativa."
        )

    return categoria_id


# ============================================================
# PRODUTOS
# ============================================================

def validar_dados_produto(dados, atualizacao=False):
    if not isinstance(dados, dict):
        raise InventoryServiceError(
            "Dados do produto inválidos."
        )

    if "ativo" in dados:
        raise InventoryServiceError(
            "O estado do produto deve ser alterado "
            "pela ação de ativar ou inativar."
        )

    campos_obrigatorios = (
        "nome",
        "unidade",
        "estoque_minimo"
    )

    if not atualizacao:
        for campo in campos_obrigatorios:
            if campo not in dados:
                raise InventoryServiceError(
                    f"O campo {campo} é obrigatório."
                )

    dados = dados.copy()

    campos_texto = (
        "nome",
        "descricao",
        "unidade"
    )

    for campo in campos_texto:
        if campo in dados:
            dados[campo] = _validar_texto(
                dados[campo],
                campo,
                obrigatorio=(
                    campo in ("nome", "unidade")
                    and not atualizacao
                )
            )

    if atualizacao:
        for campo in ("nome", "unidade"):
            if campo in dados and not dados[campo]:
                raise InventoryServiceError(
                    f"O campo {campo} não pode ser vazio."
                )

    if "categoria_id" in dados or "categoria_nome" in dados:
        if "categoria_id" in dados:
            dados["categoria_id"] = validar_categoria(
                dados["categoria_id"]
            )

    if "estoque_minimo" in dados:
        minimo = _converter_decimal(
            dados["estoque_minimo"],
            "estoque mínimo"
        )

        if minimo < 0:
            raise InventoryServiceError(
                "O estoque mínimo não pode ser negativo."
            )

        dados["estoque_minimo"] = minimo

    if "controla_lote_validade" in dados:
        valor = dados["controla_lote_validade"]

        if valor in (True, 1, "1", "true", "True", "on"):
            dados["controla_lote_validade"] = 1
        elif valor in (
            False, 0, "0", "false", "False", "", None
        ):
            dados["controla_lote_validade"] = 0
        else:
            raise InventoryServiceError(
                "A configuração de controle de lote é inválida."
            )

    else:
        if not atualizacao:
            dados["controla_lote_validade"] = 0

    return dados


def listar_produtos(
    filtros=None,
    limite=50,
    deslocamento=0
):
    if not isinstance(limite, int) or not 1 <= limite <= 100:
        raise InventoryServiceError(
            "Limite de consulta inválido."
        )

    if not isinstance(deslocamento, int) or deslocamento < 0:
        raise InventoryServiceError(
            "Deslocamento inválido."
        )

    return inventory_repository.listar_produtos(
        filtros=filtros,
        limite=limite,
        deslocamento=deslocamento
    )


def contar_produtos(filtros=None):
    return inventory_repository.contar_produtos(filtros)


def buscar_produto(produto_id):
    produto_id = _validar_id(
        produto_id,
        "produto"
    )

    produto = inventory_repository.buscar_produto_por_id(
        produto_id
    )

    if not produto:
        raise InventoryServiceError(
            "Produto não encontrado."
        )

    return produto


def cadastrar_produto(dados, criado_por):
    dados = validar_dados_produto(dados)

    try:
        return inventory_repository.criar_produto(
            dados=dados,
            criado_por=criado_por
        )
    except Exception as erro:
        _tratar_erro_repositorio(erro)


def editar_produto(produto_id, dados):
    produto = buscar_produto(produto_id)

    dados = validar_dados_produto(
        dados,
        atualizacao=True
    )

    if "controla_lote_validade" in dados:
        novo_controle = int(
            dados["controla_lote_validade"]
        )

        controle_atual = int(
            produto["controla_lote_validade"]
        )

        if novo_controle != controle_atual:
            lotes = inventory_repository.listar_lotes_produto(
                produto_id
            )

            movimentacoes = (
                inventory_repository.contar_movimentacoes(
                    produto_id=produto_id
                )
            )

            if lotes or movimentacoes:
                raise InventoryServiceError(
                    "Não é possível alterar o controle de lote "
                    "de um produto que possui histórico."
                )

    try:
        atualizado = inventory_repository.atualizar_produto(
            produto_id,
            dados
        )
    except Exception as erro:
        _tratar_erro_repositorio(erro)

    if not atualizado:
        raise InventoryServiceError(
            "Não foi possível atualizar o produto."
        )

    return True


def inativar_produto(produto_id):
    buscar_produto(produto_id)

    try:
        atualizado = inventory_repository.alterar_status_produto(
            produto_id,
            0
        )
    except Exception as erro:
        _tratar_erro_repositorio(erro)

    if not atualizado:
        raise InventoryServiceError(
            "Não foi possível inativar o produto."
        )

    return True


def reativar_produto(produto_id):
    produto = buscar_produto(produto_id)

    if int(produto["ativo"]) == 1:
        raise InventoryServiceError(
            "O produto já está ativo."
        )

    try:
        atualizado = inventory_repository.alterar_status_produto(
            produto_id,
            1
        )
    except Exception as erro:
        _tratar_erro_repositorio(erro)

    if not atualizado:
        raise InventoryServiceError(
            "Não foi possível reativar o produto."
        )

    return True


# ============================================================
# EXCLUSÃO DE PRODUTOS
# ============================================================

def verificar_exclusao_produto(produto_id):
    """
    Valida o produto e retorna a quantidade de registros vinculados.

    A existência de vínculos não impede a exclusão definitiva:
    o repositório será responsável por removê-los na transação.
    """
    produto_id = _validar_id(
        produto_id,
        "produto"
    )

    buscar_produto(produto_id)

    try:
        vinculos = inventory_repository.verificar_vinculos_produto(
            produto_id
        )
    except Exception as erro:
        _tratar_erro_repositorio(erro)

    return {
        "lotes": int(vinculos.get("lotes", 0) or 0),
        "movimentacoes": int(vinculos.get("movimentacoes", 0) or 0),
        "atividades": int(vinculos.get("atividades", 0) or 0),
        "aulas": int(vinculos.get("aulas", 0) or 0),
        "possui_vinculos": bool(vinculos.get("possui_vinculos", False)),
        "pode_excluir": True
    }


def excluir_produto(produto_id, excluido_por):
    """
    Valida os identificadores e delega a exclusão definitiva
    ao repositório, que deve executar a operação e a auditoria
    dentro de uma única transação.
    """
    produto_id = _validar_id(
        produto_id,
        "produto"
    )

    excluido_por = _validar_id(
        excluido_por,
        "responsável pela exclusão"
    )

    try:
        excluido = inventory_repository.excluir_produto(
            produto_id=produto_id,
            excluido_por=excluido_por
        )
    except Exception as erro:
        _tratar_erro_repositorio(erro)

    if not excluido:
        raise InventoryServiceError(
            "Não foi possível excluir o produto."
        )

    return True


# ============================================================
# LOTES
# ============================================================

def listar_lotes_produto(produto_id):
    buscar_produto(produto_id)

    return inventory_repository.listar_lotes_produto(
        produto_id
    )


def validar_dados_lote(dados):
    if not isinstance(dados, dict):
        raise InventoryServiceError(
            "Dados do lote inválidos."
        )

    produto_id = _validar_id(
        dados.get("produto_id"),
        "produto"
    )

    produto = buscar_produto(produto_id)

    if int(produto["ativo"]) != 1:
        raise InventoryServiceError(
            "Não é possível criar lote para produto inativo."
        )

    if int(produto["controla_lote_validade"]) != 1:
        raise InventoryServiceError(
            "Este produto não utiliza controle de lote."
        )

    quantidade = _validar_quantidade(
        dados.get("quantidade_inicial")
    )

    validade = dados.get("validade")

    if validade:
        try:
            validade_convertida = datetime.strptime(
                str(validade),
                "%Y-%m-%d"
            ).date()
        except ValueError:
            raise InventoryServiceError(
                "A data de validade é inválida."
            )

        if validade_convertida < date.today():
            raise InventoryServiceError(
                "A validade informada já expirou."
            )

    return {
        "produto_id": produto_id,
        "codigo_lote": _validar_texto(
            dados.get("codigo_lote"),
            "código do lote"
        ),
        "validade": validade or None,
        "quantidade_inicial": quantidade
    }


def cadastrar_lote(dados, responsavel_id):
    dados = validar_dados_lote(dados)

    responsavel_id = _validar_id(
        responsavel_id,
        "responsável"
    )

    try:
        return inventory_repository.criar_lote_com_entrada_atomica(
            dados,
            responsavel_id
        )
    except Exception as erro:
        _tratar_erro_repositorio(erro)


# ============================================================
# MOVIMENTAÇÕES
# ============================================================

def listar_movimentacoes(
    produto_id=None,
    tipo=None,
    limite=50,
    deslocamento=0
):
    if not isinstance(limite, int) or not 1 <= limite <= 100:
        raise InventoryServiceError(
            "Limite de consulta inválido."
        )

    if not isinstance(deslocamento, int) or deslocamento < 0:
        raise InventoryServiceError(
            "Deslocamento inválido."
        )

    if produto_id is not None:
        produto_id = _validar_id(
            produto_id,
            "produto"
        )

    if tipo not in (
        None, "", "entrada", "saida", "ajuste"
    ):
        raise InventoryServiceError(
            "Tipo de movimentação inválido."
        )

    return inventory_repository.listar_movimentacoes(
        produto_id=produto_id,
        tipo=tipo or None,
        limite=limite,
        deslocamento=deslocamento
    )


def contar_movimentacoes(produto_id=None, tipo=None):
    if produto_id is not None:
        produto_id = _validar_id(
            produto_id,
            "produto"
        )

    if tipo not in (
        None, "", "entrada", "saida", "ajuste"
    ):
        raise InventoryServiceError(
            "Tipo de movimentação inválido."
        )

    return inventory_repository.contar_movimentacoes(
        produto_id=produto_id,
        tipo=tipo or None
    )


def buscar_saldo_produto(produto_id):
    produto = buscar_produto(produto_id)

    return produto["quantidade_atual"]


def registrar_movimentacao(dados, responsavel_id):
    if not isinstance(dados, dict):
        raise InventoryServiceError(
            "Dados da movimentação inválidos."
        )

    produto_id = _validar_id(
        dados.get("produto_id"),
        "produto"
    )

    produto = buscar_produto(produto_id)

    if int(produto["ativo"]) != 1:
        raise InventoryServiceError(
            "Não é possível movimentar um produto inativo."
        )

    tipo = str(
        dados.get("tipo", "")
    ).strip().lower()

    if tipo not in ("entrada", "saida", "ajuste"):
        raise InventoryServiceError(
            "O tipo deve ser entrada, saída ou ajuste."
        )

    quantidade = _validar_quantidade(
        dados.get("quantidade")
    )

    motivo = _validar_texto(
        dados.get("motivo"),
        "motivo",
        obrigatorio=True
    )

    sentido_ajuste = None

    if tipo == "ajuste":
        sentido_ajuste = str(
            dados.get("sentido_ajuste", "")
        ).strip().lower()

        if sentido_ajuste not in (
            "acrescimo",
            "reducao"
        ):
            raise InventoryServiceError(
                "Informe se o ajuste será de acréscimo ou redução."
            )

    lote_id = dados.get("lote_id")

    controla_lote = int(
        produto["controla_lote_validade"]
    ) == 1

    if controla_lote and not lote_id:
        raise InventoryServiceError(
            "Selecione o lote para este produto."
        )

    if not controla_lote and lote_id:
        raise InventoryServiceError(
            "Este produto não utiliza controle de lote."
        )

    if lote_id:
        lote_id = _validar_id(
            lote_id,
            "lote"
        )

        lote = inventory_repository.buscar_lote_por_id(
            lote_id
        )

        if (
            not lote
            or int(lote["produto_id"]) != produto_id
        ):
            raise InventoryServiceError(
                "O lote selecionado não pertence ao produto."
            )

    data_hora = dados.get("data_hora")

    if data_hora:
        try:
            datetime.strptime(
                str(data_hora),
                "%Y-%m-%dT%H:%M"
            )
        except ValueError:
            raise InventoryServiceError(
                "A data e hora da movimentação são inválidas."
            )

    responsavel_id = _validar_id(
        responsavel_id,
        "responsável"
    )

    movimento = {
        "produto_id": produto_id,
        "lote_id": lote_id,
        "tipo": tipo,
        "sentido_ajuste": sentido_ajuste,
        "quantidade": quantidade,
        "data_hora": data_hora or None,
        "responsavel_id": responsavel_id,
        "motivo": motivo
    }

    try:
        return inventory_repository.registrar_movimentacao_atomica(
            movimento
        )
    except Exception as erro:
        _tratar_erro_repositorio(erro)