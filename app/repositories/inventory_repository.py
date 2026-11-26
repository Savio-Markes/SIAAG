# Desenvolvido por: Fábio Barbosa

from decimal import Decimal, InvalidOperation

from app.extensions import get_db


class InventoryRepositoryError(Exception):
    """Erro relacionado às operações do repositório de estoque."""
    pass


# ============================================================
# CATEGORIAS
# ============================================================

def listar_categorias(apenas_ativas=True):
    consulta = """
        SELECT id, nome, ativa
        FROM categorias_produto
    """

    if apenas_ativas:
        consulta += " WHERE ativa = 1"

    consulta += " ORDER BY nome ASC"

    conexao = get_db()

    with conexao.cursor() as cursor:
        cursor.execute(consulta)
        return cursor.fetchall()


def buscar_categoria_por_id(categoria_id):
    conexao = get_db()

    with conexao.cursor() as cursor:
        cursor.execute(
            """
            SELECT id, nome, ativa
            FROM categorias_produto
            WHERE id = %s
            """,
            (categoria_id,)
        )
        return cursor.fetchone()


def _resolver_categoria_id(cursor, dados):
    if "categoria_nome" in dados:
        nome = dados.get("categoria_nome")

        if nome is None or not str(nome).strip():
            return None

        nome = str(nome).strip()

        cursor.execute(
            """
            SELECT id, nome, ativa
            FROM categorias_produto
            WHERE LOWER(TRIM(nome)) = LOWER(%s)
            LIMIT 1
            FOR UPDATE
            """,
            (nome,)
        )

        categoria = cursor.fetchone()

        if categoria:
            if int(categoria["ativa"]) != 1:
                raise InventoryRepositoryError(
                    "A categoria informada está inativa."
                )

            return categoria["id"]

        cursor.execute(
            """
            INSERT INTO categorias_produto (nome, ativa)
            VALUES (%s, 1)
            """,
            (nome,)
        )

        return cursor.lastrowid

    categoria_id = dados.get("categoria_id")

    if categoria_id in (None, ""):
        return None

    cursor.execute(
        """
        SELECT id, ativa
        FROM categorias_produto
        WHERE id = %s
        FOR UPDATE
        """,
        (categoria_id,)
    )

    categoria = cursor.fetchone()

    if not categoria:
        raise InventoryRepositoryError(
            "A categoria informada não existe."
        )

    if int(categoria["ativa"]) != 1:
        raise InventoryRepositoryError(
            "A categoria selecionada está inativa."
        )

    return categoria_id


# ============================================================
# PRODUTOS
# ============================================================

def _montar_condicoes(filtros=None):
    filtros = filtros or {}

    condicoes = ["1 = 1"]
    parametros = []

    if filtros.get("busca"):
        condicoes.append("p.nome LIKE %s")
        parametros.append(f"%{filtros['busca']}%")

    if filtros.get("categoria_id"):
        condicoes.append("p.categoria_id = %s")
        parametros.append(filtros["categoria_id"])

    if filtros.get("ativo") in (0, 1, "0", "1"):
        condicoes.append("p.ativo = %s")
        parametros.append(int(filtros["ativo"]))

    return " AND ".join(condicoes), parametros


def _consulta_saldo():
    """
    Produtos com lote:
        Saldo materializado em lotes_produto.

    Produtos sem lote:
        Entradas - saídas + acréscimos - reduções.
    """

    return """
        CASE
            WHEN p.controla_lote_validade = 1 THEN
                COALESCE(
                    (
                        SELECT SUM(lp.saldo_atual)
                        FROM lotes_produto lp
                        WHERE lp.produto_id = p.id
                    ),
                    0
                )
            ELSE
                COALESCE(
                    (
                        SELECT SUM(
                            CASE
                                WHEN me.tipo = 'entrada'
                                    THEN me.quantidade

                                WHEN me.tipo = 'saida'
                                    THEN -me.quantidade

                                WHEN me.tipo = 'ajuste'
                                     AND me.sentido_ajuste = 'acrescimo'
                                    THEN me.quantidade

                                WHEN me.tipo = 'ajuste'
                                     AND me.sentido_ajuste = 'reducao'
                                    THEN -me.quantidade

                                ELSE 0
                            END
                        )
                        FROM movimentacoes_estoque me
                        WHERE me.produto_id = p.id
                    ),
                    0
                )
        END
    """


def listar_produtos(
    filtros=None,
    limite=50,
    deslocamento=0
):
    condicoes, parametros = _montar_condicoes(filtros)
    saldo_sql = _consulta_saldo()

    consulta = f"""
        SELECT
            p.id,
            p.nome,
            p.categoria_id,
            cp.nome AS categoria_nome,
            p.descricao,
            p.unidade,
            p.estoque_minimo,
            p.controla_lote_validade,
            p.ativo,
            p.criado_por,
            p.criado_em,
            p.atualizado_em,
            ({saldo_sql}) AS quantidade_atual
        FROM produtos p
        LEFT JOIN categorias_produto cp
            ON cp.id = p.categoria_id
        WHERE {condicoes}
        ORDER BY p.nome ASC
        LIMIT %s OFFSET %s
    """

    parametros.extend([limite, deslocamento])

    conexao = get_db()

    with conexao.cursor() as cursor:
        cursor.execute(consulta, parametros)
        return cursor.fetchall()


def contar_produtos(filtros=None):
    condicoes, parametros = _montar_condicoes(filtros)

    consulta = f"""
        SELECT COUNT(*) AS total
        FROM produtos p
        WHERE {condicoes}
    """

    conexao = get_db()

    with conexao.cursor() as cursor:
        cursor.execute(consulta, parametros)
        return cursor.fetchone()["total"]


def buscar_produto_por_id(produto_id):
    saldo_sql = _consulta_saldo()

    consulta = f"""
        SELECT
            p.*,
            cp.nome AS categoria_nome,
            ({saldo_sql}) AS quantidade_atual
        FROM produtos p
        LEFT JOIN categorias_produto cp
            ON cp.id = p.categoria_id
        WHERE p.id = %s
        LIMIT 1
    """

    conexao = get_db()

    with conexao.cursor() as cursor:
        cursor.execute(consulta, (produto_id,))
        return cursor.fetchone()


def criar_produto(dados, criado_por):
    conexao = get_db()

    try:
        with conexao.cursor() as cursor:
            categoria_id = _resolver_categoria_id(
                cursor,
                dados
            )

            cursor.execute(
                """
                INSERT INTO produtos (
                    nome,
                    categoria_id,
                    descricao,
                    unidade,
                    estoque_minimo,
                    controla_lote_validade,
                    ativo,
                    criado_por,
                    criado_em,
                    atualizado_em
                ) VALUES (
                    %s, %s, %s, %s, %s,
                    %s, 1, %s, NOW(), NOW()
                )
                """,
                (
                    dados["nome"],
                    categoria_id,
                    dados.get("descricao"),
                    dados["unidade"],
                    dados["estoque_minimo"],
                    dados.get("controla_lote_validade", 0),
                    criado_por
                )
            )

            produto_id = cursor.lastrowid

        conexao.commit()
        return produto_id

    except Exception:
        conexao.rollback()
        raise


def atualizar_produto(produto_id, dados):
    campos_permitidos = (
        "nome",
        "descricao",
        "unidade",
        "estoque_minimo",
        "controla_lote_validade"
    )

    conexao = get_db()

    try:
        with conexao.cursor() as cursor:
            cursor.execute(
                """
                SELECT id
                FROM produtos
                WHERE id = %s
                FOR UPDATE
                """,
                (produto_id,)
            )

            if not cursor.fetchone():
                raise InventoryRepositoryError(
                    "Produto não encontrado."
                )

            campos = []
            parametros = []

            if (
                "categoria_nome" in dados
                or "categoria_id" in dados
            ):
                categoria_id = _resolver_categoria_id(
                    cursor,
                    dados
                )

                campos.append("categoria_id = %s")
                parametros.append(categoria_id)

            for campo in campos_permitidos:
                if campo in dados:
                    campos.append(f"{campo} = %s")
                    parametros.append(dados[campo])

            if campos:
                campos.append("atualizado_em = NOW()")

                consulta = f"""
                    UPDATE produtos
                    SET {", ".join(campos)}
                    WHERE id = %s
                """

                parametros.append(produto_id)
                cursor.execute(consulta, parametros)

        conexao.commit()
        return True

    except Exception:
        conexao.rollback()
        raise


def alterar_status_produto(produto_id, ativo):
    conexao = get_db()

    try:
        with conexao.cursor() as cursor:
            cursor.execute(
                """
                UPDATE produtos
                SET ativo = %s,
                    atualizado_em = NOW()
                WHERE id = %s
                """,
                (int(ativo), produto_id)
            )

            atualizado = cursor.rowcount > 0

        conexao.commit()
        return atualizado

    except Exception:
        conexao.rollback()
        raise


# ============================================================
# EXCLUSÃO DE PRODUTOS
# ============================================================

def verificar_vinculos_produto(produto_id, cursor=None):
    """
    Conta os vínculos diretos e indiretos de um produto.
    """

    conexao = get_db() if cursor is None else None

    def consultar_vinculos(cursor_atual):
        cursor_atual.execute(
            """
            SELECT COUNT(*) AS total
            FROM lotes_produto
            WHERE produto_id = %s
            """,
            (produto_id,)
        )
        lotes = cursor_atual.fetchone()["total"]

        cursor_atual.execute(
            """
            SELECT COUNT(*) AS total
            FROM movimentacoes_estoque
            WHERE produto_id = %s
            """,
            (produto_id,)
        )
        movimentacoes = cursor_atual.fetchone()["total"]

        cursor_atual.execute(
            """
            SELECT COUNT(DISTINCT ai.id) AS total
            FROM atividade_insumos ai
            WHERE ai.produto_id = %s
               OR ai.lote_id IN (
                    SELECT lp.id
                    FROM lotes_produto lp
                    WHERE lp.produto_id = %s
               )
               OR ai.movimentacao_id IN (
                    SELECT me.id
                    FROM movimentacoes_estoque me
                    WHERE me.produto_id = %s
               )
            """,
            (produto_id, produto_id, produto_id)
        )
        atividades = cursor_atual.fetchone()["total"]

        cursor_atual.execute(
            """
            SELECT COUNT(DISTINCT ra.id) AS total
            FROM recursos_aula ra
            WHERE ra.produto_id = %s
               OR ra.movimentacao_id IN (
                    SELECT me.id
                    FROM movimentacoes_estoque me
                    WHERE me.produto_id = %s
               )
            """,
            (produto_id, produto_id)
        )
        aulas = cursor_atual.fetchone()["total"]

        resultado = {
            "lotes": lotes,
            "movimentacoes": movimentacoes,
            "atividades": atividades,
            "aulas": aulas
        }

        resultado["possui_vinculos"] = any(
            quantidade > 0
            for quantidade in resultado.values()
        )

        return resultado

    if cursor is not None:
        return consultar_vinculos(cursor)

    with conexao.cursor() as cursor_atual:
        return consultar_vinculos(cursor_atual)


def excluir_produto(
    produto_id,
    excluido_por,
    justificativa
):
    """
    Exclui definitivamente o cadastro do produto,
    preservando os registros históricos e sua justificativa.
    """

    justificativa = str(justificativa or "").strip()

    if not justificativa:
        raise InventoryRepositoryError(
            "Informe a justificativa da exclusão."
        )

    if len(justificativa) > 500:
        raise InventoryRepositoryError(
            "A justificativa deve ter no máximo 500 caracteres."
        )

    conexao = get_db()

    try:
        with conexao.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, nome, unidade, controla_lote_validade
                FROM produtos
                WHERE id = %s
                FOR UPDATE
                """,
                (produto_id,)
            )

            produto = cursor.fetchone()

            if not produto:
                raise InventoryRepositoryError(
                    "Produto não encontrado."
                )

            nome = produto["nome"]
            unidade = produto["unidade"]

            controla_lote = (
                int(produto["controla_lote_validade"]) == 1
            )

            vinculos = verificar_vinculos_produto(
                produto_id,
                cursor=cursor
            )

            # Calcula o saldo antes da exclusão.
            if controla_lote:
                cursor.execute(
                    """
                    SELECT COALESCE(SUM(saldo_atual), 0) AS saldo
                    FROM lotes_produto
                    WHERE produto_id = %s
                    """,
                    (produto_id,)
                )
            else:
                cursor.execute(
                    """
                    SELECT COALESCE(
                        SUM(
                            CASE
                                WHEN tipo = 'entrada'
                                    THEN quantidade

                                WHEN tipo = 'saida'
                                    THEN -quantidade

                                WHEN tipo = 'ajuste'
                                     AND sentido_ajuste = 'acrescimo'
                                    THEN quantidade

                                WHEN tipo = 'ajuste'
                                     AND sentido_ajuste = 'reducao'
                                    THEN -quantidade

                                ELSE 0
                            END
                        ),
                        0
                    ) AS saldo
                    FROM movimentacoes_estoque
                    WHERE produto_id = %s
                    """,
                    (produto_id,)
                )

            saldo = Decimal(
                str(cursor.fetchone()["saldo"] or 0)
            )

            # Preserva os dados das movimentações.
            cursor.execute(
                """
                UPDATE movimentacoes_estoque me
                LEFT JOIN lotes_produto lp
                    ON lp.id = me.lote_id
                SET
                    me.produto_nome = COALESCE(
                        me.produto_nome, %s
                    ),
                    me.unidade = COALESCE(
                        me.unidade, %s
                    ),
                    me.lote_codigo = COALESCE(
                        lp.codigo_lote,
                        me.lote_codigo
                    ),
                    me.lote_id = NULL
                WHERE me.produto_id = %s
                """,
                (nome, unidade, produto_id)
            )

            # Preserva nome e unidade nos insumos das atividades.
            cursor.execute(
                """
                UPDATE atividade_insumos ai
                LEFT JOIN lotes_produto lp
                    ON lp.id = ai.lote_id
                LEFT JOIN movimentacoes_estoque me
                    ON me.id = ai.movimentacao_id
                SET
                    ai.produto_nome = COALESCE(
                        ai.produto_nome,
                        me.produto_nome,
                        %s
                    ),
                    ai.unidade = COALESCE(
                        ai.unidade,
                        me.unidade,
                        %s
                    ),
                    ai.produto_id = NULL,
                    ai.lote_id = NULL,
                    ai.movimentacao_id = NULL
                WHERE ai.produto_id = %s
                   OR lp.produto_id = %s
                   OR me.produto_id = %s
                """,
                (
                    nome,
                    unidade,
                    produto_id,
                    produto_id,
                    produto_id
                )
            )

            atividades_desvinculadas = cursor.rowcount

            # Preserva nome e unidade nos recursos das aulas.
            cursor.execute(
                """
                UPDATE recursos_aula ra
                LEFT JOIN movimentacoes_estoque me
                    ON me.id = ra.movimentacao_id
                SET
                    ra.produto_nome = COALESCE(
                        ra.produto_nome,
                        me.produto_nome,
                        %s
                    ),
                    ra.unidade = COALESCE(
                        ra.unidade,
                        me.unidade,
                        %s
                    ),
                    ra.produto_id = NULL,
                    ra.movimentacao_id = NULL
                WHERE ra.produto_id = %s
                   OR me.produto_id = %s
                """,
                (
                    nome,
                    unidade,
                    produto_id,
                    produto_id
                )
            )

            recursos_aula_desvinculados = cursor.rowcount

            # Registra o evento de exclusão.
            # produto_id fica NULL porque o cadastro será removido.
            cursor.execute(
                """
                INSERT INTO movimentacoes_estoque (
                    produto_id,
                    lote_id,
                    produto_nome,
                    unidade,
                    lote_codigo,
                    tipo,
                    sentido_ajuste,
                    quantidade,
                    data_hora,
                    responsavel_id,
                    motivo
                ) VALUES (
                    NULL, NULL, %s, %s, NULL,
                    'exclusao', NULL, %s, NOW(), %s, %s
                )
                """,
                (
                    nome,
                    unidade,
                    saldo,
                    excluido_por,
                    justificativa
                )
            )

            movimentacao_exclusao_id = cursor.lastrowid

            # Remove os lotes após preservar os históricos.
            cursor.execute(
                """
                DELETE FROM lotes_produto
                WHERE produto_id = %s
                """,
                (produto_id,)
            )

            lotes_removidos = cursor.rowcount

            # Remove o cadastro do produto por último.
            cursor.execute(
                """
                DELETE FROM produtos
                WHERE id = %s
                """,
                (produto_id,)
            )

            if cursor.rowcount != 1:
                raise InventoryRepositoryError(
                    "Não foi possível concluir a exclusão do produto."
                )

            # Registra a operação na auditoria.
            detalhes = (
                f"Produto '{nome}' (ID {produto_id}) "
                f"excluído definitivamente. "
                f"Saldo registrado: {saldo} {unidade}. "
                f"Justificativa: {justificativa}. "
                f"Movimentação de exclusão: "
                f"{movimentacao_exclusao_id}. "
                f"Lotes removidos: {lotes_removidos}. "
                f"Atividades preservadas: "
                f"{atividades_desvinculadas}. "
                f"Recursos de aulas preservados: "
                f"{recursos_aula_desvinculados}. "
                f"Movimentações históricas preservadas: "
                f"{vinculos['movimentacoes']}."
            )

            cursor.execute(
                """
                INSERT INTO logs_auditoria (
                    usuario_id,
                    data_hora,
                    modulo,
                    acao,
                    entidade,
                    registro_id,
                    resultado,
                    detalhes_resumidos
                ) VALUES (
                    %s, NOW(), 'estoque',
                    'excluir_produto',
                    'produtos',
                    %s, 'sucesso', %s
                )
                """,
                (
                    excluido_por,
                    produto_id,
                    detalhes
                )
            )

        conexao.commit()
        return True

    except Exception:
        conexao.rollback()
        raise


# ============================================================
# LOTES
# ============================================================

def listar_lotes_produto(produto_id):
    consulta = """
        SELECT
            id,
            produto_id,
            codigo_lote,
            validade,
            quantidade_inicial,
            saldo_atual
        FROM lotes_produto
        WHERE produto_id = %s
        ORDER BY validade ASC, id ASC
    """

    conexao = get_db()

    with conexao.cursor() as cursor:
        cursor.execute(consulta, (produto_id,))
        return cursor.fetchall()


def buscar_lote_por_id(lote_id):
    conexao = get_db()

    with conexao.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                id,
                produto_id,
                codigo_lote,
                validade,
                quantidade_inicial,
                saldo_atual
            FROM lotes_produto
            WHERE id = %s
            """,
            (lote_id,)
        )
        return cursor.fetchone()


def criar_lote_com_entrada_atomica(dados, responsavel_id):
    """
    Cria o lote, registra sua entrada inicial e registra
    a auditoria em uma única transação.
    """

    quantidade = Decimal(str(dados["quantidade_inicial"]))

    conexao = get_db()

    try:
        with conexao.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, ativo, controla_lote_validade
                FROM produtos
                WHERE id = %s
                FOR UPDATE
                """,
                (dados["produto_id"],)
            )

            produto = cursor.fetchone()

            if not produto:
                raise InventoryRepositoryError(
                    "Produto não encontrado."
                )

            if int(produto["ativo"]) != 1:
                raise InventoryRepositoryError(
                    "Não é possível criar lote para produto inativo."
                )

            if int(produto["controla_lote_validade"]) != 1:
                raise InventoryRepositoryError(
                    "Este produto não utiliza controle de lote."
                )

            cursor.execute(
                """
                INSERT INTO lotes_produto (
                    produto_id,
                    codigo_lote,
                    validade,
                    quantidade_inicial,
                    saldo_atual
                ) VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    dados["produto_id"],
                    dados.get("codigo_lote"),
                    dados.get("validade"),
                    quantidade,
                    quantidade
                )
            )

            lote_id = cursor.lastrowid

            cursor.execute(
                """
                INSERT INTO movimentacoes_estoque (
                    produto_id,
                    lote_id,
                    tipo,
                    sentido_ajuste,
                    quantidade,
                    data_hora,
                    responsavel_id,
                    motivo
                ) VALUES (
                    %s, %s, 'entrada', NULL,
                    %s, NOW(), %s, %s
                )
                """,
                (
                    dados["produto_id"],
                    lote_id,
                    quantidade,
                    responsavel_id,
                    "Entrada inicial do lote."
                )
            )

            movimentacao_id = cursor.lastrowid

            cursor.execute(
                """
                INSERT INTO logs_auditoria (
                    usuario_id,
                    data_hora,
                    modulo,
                    acao,
                    entidade,
                    registro_id,
                    resultado,
                    detalhes_resumidos
                ) VALUES (
                    %s, NOW(), 'estoque',
                    'cadastrar_lote',
                    'lotes_produto',
                    %s, 'sucesso', %s
                )
                """,
                (
                    responsavel_id,
                    lote_id,
                    (
                        f"Lote {lote_id} criado para o produto "
                        f"{dados['produto_id']}. "
                        f"Entrada inicial: {quantidade}."
                    )
                )
            )

        conexao.commit()

        return {
            "lote_id": lote_id,
            "movimentacao_id": movimentacao_id
        }

    except Exception:
        conexao.rollback()
        raise


# Compatibilidade temporária com chamadas antigas.
# O cadastro definitivo deve usar criar_lote_com_entrada_atomica.

def criar_lote(dados):
    raise InventoryRepositoryError(
        "Utilize o cadastro atômico de lotes."
    )


# ============================================================
# MOVIMENTAÇÕES
# ============================================================

def listar_movimentacoes(
    produto_id=None,
    tipo=None,
    limite=50,
    deslocamento=0
):
    condicoes = ["1 = 1"]
    parametros = []

    if produto_id is not None:
        condicoes.append("me.produto_id = %s")
        parametros.append(produto_id)

    if tipo:
        condicoes.append("me.tipo = %s")
        parametros.append(tipo)

    consulta = f"""
        SELECT
            me.id,
            me.produto_id,
            COALESCE(
                me.produto_nome,
                p.nome
            ) AS produto_nome,
            COALESCE(
                me.unidade,
                p.unidade
            ) AS unidade,
            me.lote_id,
            COALESCE(
                me.lote_codigo,
                lp.codigo_lote
            ) AS lote_codigo,
            me.tipo,
            me.sentido_ajuste,
            me.quantidade,
            me.data_hora,
            me.responsavel_id,
            u.nome AS responsavel_nome,
            me.motivo
        FROM movimentacoes_estoque me
        LEFT JOIN produtos p
            ON p.id = me.produto_id
        LEFT JOIN lotes_produto lp
            ON lp.id = me.lote_id
        LEFT JOIN usuarios u
            ON u.id = me.responsavel_id
        WHERE {" AND ".join(condicoes)}
        ORDER BY me.data_hora DESC, me.id DESC
        LIMIT %s OFFSET %s
    """

    parametros.extend([limite, deslocamento])

    conexao = get_db()

    with conexao.cursor() as cursor:
        cursor.execute(consulta, parametros)
        return cursor.fetchall()


def contar_movimentacoes(produto_id=None, tipo=None):
    condicoes = ["1 = 1"]
    parametros = []

    if produto_id is not None:
        condicoes.append("produto_id = %s")
        parametros.append(produto_id)

    if tipo:
        condicoes.append("tipo = %s")
        parametros.append(tipo)

    consulta = f"""
        SELECT COUNT(*) AS total
        FROM movimentacoes_estoque
        WHERE {" AND ".join(condicoes)}
    """

    conexao = get_db()

    with conexao.cursor() as cursor:
        cursor.execute(consulta, parametros)
        return cursor.fetchone()["total"]


def buscar_saldo_produto(produto_id):
    produto = buscar_produto_por_id(produto_id)

    if not produto:
        return None

    return produto["quantidade_atual"]


# ============================================================
# AUDITORIA
# ============================================================

def registrar_auditoria(
    usuario_id,
    acao,
    entidade,
    registro_id,
    detalhes
):
    consulta = """
        INSERT INTO logs_auditoria (
            usuario_id,
            data_hora,
            modulo,
            acao,
            entidade,
            registro_id,
            resultado,
            detalhes_resumidos
        ) VALUES (
            %s, NOW(), 'estoque', %s, %s, %s, 'sucesso', %s
        )
    """

    conexao = get_db()

    try:
        with conexao.cursor() as cursor:
            cursor.execute(
                consulta,
                (
                    usuario_id,
                    acao,
                    entidade,
                    registro_id,
                    detalhes
                )
            )

        conexao.commit()
        return True

    except Exception:
        conexao.rollback()
        raise


# ============================================================
# MOVIMENTAÇÃO ATÔMICA
# ============================================================

def registrar_movimentacao_atomica(dados):
    """
    Registra entrada, saída ou ajuste.

    Ajuste:
        quantidade sempre positiva;
        sentido_ajuste = acrescimo ou reducao.

    Para produtos com lote, atualiza saldo_atual.
    Para produtos sem lote, o saldo é calculado pelo histórico.
    """

    quantidade = Decimal(str(dados["quantidade"]))

    if not quantidade.is_finite() or quantidade <= 0:
        raise InventoryRepositoryError(
            "A quantidade deve ser maior que zero."
        )

    tipo = dados["tipo"]
    sentido = dados.get("sentido_ajuste")

    if tipo not in ("entrada", "saida", "ajuste"):
        raise InventoryRepositoryError(
            "Tipo de movimentação inválido."
        )

    if tipo == "ajuste":
        if sentido not in ("acrescimo", "reducao"):
            raise InventoryRepositoryError(
                "Informe se o ajuste é acréscimo ou redução."
            )
    elif sentido is not None:
        raise InventoryRepositoryError(
            "O sentido do ajuste só pode ser informado em ajustes."
        )

    conexao = get_db()

    try:
        with conexao.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, ativo, controla_lote_validade
                FROM produtos
                WHERE id = %s
                FOR UPDATE
                """,
                (dados["produto_id"],)
            )

            produto = cursor.fetchone()

            if not produto:
                raise InventoryRepositoryError(
                    "Produto não encontrado."
                )

            if int(produto["ativo"]) != 1:
                raise InventoryRepositoryError(
                    "Produto inativo."
                )

            controla_lote = (
                int(produto["controla_lote_validade"]) == 1
            )

            lote_id = dados.get("lote_id")

            if controla_lote and not lote_id:
                raise InventoryRepositoryError(
                    "Selecione o lote deste produto."
                )

            if not controla_lote and lote_id:
                raise InventoryRepositoryError(
                    "Este produto não utiliza controle de lote."
                )

            if controla_lote:
                cursor.execute(
                    """
                    SELECT id, produto_id, saldo_atual
                    FROM lotes_produto
                    WHERE id = %s
                    FOR UPDATE
                    """,
                    (lote_id,)
                )

                lote = cursor.fetchone()

                if (
                    not lote
                    or int(lote["produto_id"]) != int(dados["produto_id"])
                ):
                    raise InventoryRepositoryError(
                        "Lote não encontrado para este produto."
                    )

                saldo_atual = Decimal(
                    str(lote["saldo_atual"] or 0)
                )

            else:
                cursor.execute(
                    """
                    SELECT COALESCE(
                        SUM(
                            CASE
                                WHEN tipo = 'entrada'
                                    THEN quantidade

                                WHEN tipo = 'saida'
                                    THEN -quantidade

                                WHEN tipo = 'ajuste'
                                     AND sentido_ajuste = 'acrescimo'
                                    THEN quantidade

                                WHEN tipo = 'ajuste'
                                     AND sentido_ajuste = 'reducao'
                                    THEN -quantidade

                                ELSE 0
                            END
                        ),
                        0
                    ) AS saldo
                    FROM movimentacoes_estoque
                    WHERE produto_id = %s
                    """,
                    (dados["produto_id"],)
                )

                resultado = cursor.fetchone()

                saldo_atual = Decimal(
                    str(resultado["saldo"] or 0)
                )

            if tipo == "entrada":
                novo_saldo = saldo_atual + quantidade

            elif tipo == "saida":
                novo_saldo = saldo_atual - quantidade

            elif sentido == "acrescimo":
                novo_saldo = saldo_atual + quantidade

            else:
                novo_saldo = saldo_atual - quantidade

            if novo_saldo < 0:
                raise InventoryRepositoryError(
                    "Saldo insuficiente para realizar a operação."
                )

            cursor.execute(
                """
                INSERT INTO movimentacoes_estoque (
                    produto_id,
                    lote_id,
                    tipo,
                    sentido_ajuste,
                    quantidade,
                    data_hora,
                    responsavel_id,
                    motivo
                ) VALUES (
                    %s, %s, %s, %s, %s,
                    COALESCE(%s, NOW()),
                    %s, %s
                )
                """,
                (
                    dados["produto_id"],
                    lote_id,
                    tipo,
                    sentido,
                    quantidade,
                    dados.get("data_hora"),
                    dados["responsavel_id"],
                    dados["motivo"]
                )
            )

            movimentacao_id = cursor.lastrowid

            if controla_lote:
                cursor.execute(
                    """
                    UPDATE lotes_produto
                    SET saldo_atual = %s
                    WHERE id = %s
                    """,
                    (novo_saldo, lote_id)
                )

            descricao = (
                f"Movimentação {tipo} do produto "
                f"{dados['produto_id']}: {quantidade}."
            )

            if tipo == "ajuste":
                descricao += f" Sentido: {sentido}."

            cursor.execute(
                """
                INSERT INTO logs_auditoria (
                    usuario_id,
                    data_hora,
                    modulo,
                    acao,
                    entidade,
                    registro_id,
                    resultado,
                    detalhes_resumidos
                ) VALUES (
                    %s, NOW(), 'estoque',
                    'movimentar_estoque',
                    'movimentacoes_estoque',
                    %s, 'sucesso', %s
                )
                """,
                (
                    dados["responsavel_id"],
                    movimentacao_id,
                    descricao
                )
            )

        conexao.commit()
        return movimentacao_id

    except Exception:
        conexao.rollback()
        raise


# ============================================================
# INDICADORES DA DASHBOARD
# ============================================================

def obter_indicadores_dashboard():
    """Obtém indicadores reais do estoque para a dashboard."""

    saldo_sql = _consulta_saldo()
    conexao = get_db()

    with conexao.cursor() as cursor:

        # Total de produtos, ativos e inativos
        cursor.execute("""
            SELECT
                COUNT(*) AS total,
                COALESCE(SUM(ativo = 1), 0) AS ativos,
                COALESCE(SUM(ativo = 0), 0) AS inativos
            FROM produtos
        """)

        resumo = cursor.fetchone()

        # Produtos ativos no limite ou abaixo do estoque mínimo
        cursor.execute(f"""
            SELECT COUNT(*) AS total
            FROM produtos p
            WHERE p.ativo = 1
              AND ({saldo_sql}) <= p.estoque_minimo
        """)

        estoque_baixo = cursor.fetchone()["total"]

        # Produtos agrupados por categoria
        cursor.execute("""
            SELECT
                COALESCE(cp.nome, 'Sem categoria') AS categoria,
                COUNT(p.id) AS total
            FROM produtos p
            LEFT JOIN categorias_produto cp
                ON cp.id = p.categoria_id
            GROUP BY cp.id, cp.nome
            ORDER BY total DESC, categoria ASC
        """)

        categorias = cursor.fetchall()

        # Quantidade de movimentações por tipo
        cursor.execute("""
            SELECT
                tipo,
                COUNT(*) AS total
            FROM movimentacoes_estoque
            GROUP BY tipo
        """)

        resultados_movimentacoes = cursor.fetchall()

    movimentacoes = {
        "entrada": 0,
        "saida": 0,
        "ajuste": 0
    }

    for item in resultados_movimentacoes:
        tipo = item["tipo"]

        if tipo in movimentacoes:
            movimentacoes[tipo] = item["total"]

    return {
        "total_produtos": resumo["total"],
        "produtos_ativos": resumo["ativos"],
        "produtos_inativos": resumo["inativos"],
        "estoque_baixo": estoque_baixo,
        "categorias_estoque": categorias,
        "movimentacoes_estoque": movimentacoes,
        "total_movimentacoes": sum(movimentacoes.values())
    }