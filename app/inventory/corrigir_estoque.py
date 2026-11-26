from pathlib import Path

ROOT = Path.cwd()


def replace_between(path, start_marker, end_marker, replacement):
    p = ROOT / path
    source = p.read_text(encoding="utf-8")
    start = source.find(start_marker)
    end = source.find(end_marker, start + len(start_marker))

    if start < 0 or end < 0:
        raise RuntimeError(
            f"Marcadores não encontrados em {path}; arquivo não foi alterado."
        )

    p.write_text(
        source[:start] + replacement.rstrip() + "\n\n" + source[end:],
        encoding="utf-8"
    )


replacement = '''def excluir_produto(produto_id, excluido_por):
    """Exclui o cadastro e preserva os históricos relacionados."""
    conexao = get_db()

    try:
        with conexao.cursor() as cursor:
            cursor.execute("""
                SELECT id, nome, unidade, controla_lote_validade
                FROM produtos
                WHERE id = %s
                FOR UPDATE
            """, (produto_id,))

            produto = cursor.fetchone()

            if not produto:
                raise InventoryRepositoryError("Produto não encontrado.")

            nome = produto["nome"]
            unidade = produto["unidade"]
            controla_lote = int(
                produto["controla_lote_validade"] or 0
            ) == 1

            cursor.execute("""
                SELECT id, codigo_lote, saldo_atual
                FROM lotes_produto
                WHERE produto_id = %s
                FOR UPDATE
            """, (produto_id,))

            lotes = cursor.fetchall()
            lote_ids = [int(x["id"]) for x in lotes]

            cursor.execute("""
                SELECT id
                FROM movimentacoes_estoque
                WHERE produto_id = %s
                FOR UPDATE
            """, (produto_id,))

            movimentos = cursor.fetchall()
            movimento_ids = [int(x["id"]) for x in movimentos]

            if controla_lote:
                saldo = sum(
                    (
                        Decimal(str(x["saldo_atual"] or 0))
                        for x in lotes
                    ),
                    Decimal("0")
                )
            else:
                cursor.execute("""
                    SELECT COALESCE(SUM(CASE
                        WHEN tipo = 'entrada' THEN quantidade
                        WHEN tipo = 'saida' THEN -quantidade
                        WHEN tipo = 'ajuste'
                            AND sentido_ajuste = 'acrescimo'
                            THEN quantidade
                        WHEN tipo = 'ajuste'
                            AND sentido_ajuste = 'reducao'
                            THEN -quantidade
                        ELSE 0
                    END), 0) AS saldo
                    FROM movimentacoes_estoque
                    WHERE produto_id = %s
                """, (produto_id,))

                saldo = Decimal(
                    str(cursor.fetchone()["saldo"] or 0)
                )

            # Preserva os dados históricos antes de remover os lotes.
            cursor.execute("""
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
                        lp.codigo_lote, me.lote_codigo
                    ),
                    me.lote_id = NULL
                WHERE me.produto_id = %s
            """, (nome, unidade, produto_id))

            # Preserva atividades e remove apenas os vínculos.
            conditions = ["produto_id = %s"]
            params = [produto_id]

            if lote_ids:
                placeholders = ",".join(
                    ["%s"] * len(lote_ids)
                )
                conditions.append(
                    f"lote_id IN ({placeholders})"
                )
                params.extend(lote_ids)

            if movimento_ids:
                placeholders = ",".join(
                    ["%s"] * len(movimento_ids)
                )
                conditions.append(
                    f"movimentacao_id IN ({placeholders})"
                )
                params.extend(movimento_ids)

            cursor.execute(
                """
                UPDATE atividade_insumos
                SET produto_id = NULL, lote_id = NULL
                WHERE
                """ + " OR ".join(conditions),
                params
            )

            atividades_desvinculadas = cursor.rowcount

            # Preserva os recursos das aulas práticas.
            cursor.execute("""
                UPDATE recursos_aula
                SET produto_id = NULL
                WHERE produto_id = %s
            """, (produto_id,))

            recursos_desvinculados = cursor.rowcount

            # Registra a exclusão no histórico de movimentações.
            cursor.execute("""
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
                )
                VALUES (
                    %s, NULL, %s, %s, NULL,
                    'exclusao', NULL, %s, NOW(), %s, %s
                )
            """, (
                produto_id,
                nome,
                unidade,
                saldo,
                excluido_por,
                "Exclusão definitiva do cadastro. "
                "Saldo no momento da exclusão."
            ))

            exclusao_mov_id = cursor.lastrowid

            # Remove os lotes e o cadastro do produto.
            cursor.execute("""
                DELETE FROM lotes_produto
                WHERE produto_id = %s
            """, (produto_id,))

            lotes_removidos = cursor.rowcount

            cursor.execute("""
                DELETE FROM produtos
                WHERE id = %s
            """, (produto_id,))

            if cursor.rowcount != 1:
                raise InventoryRepositoryError(
                    "Não foi possível concluir a exclusão do produto."
                )

            # Registra a operação na auditoria.
            detalhes = (
                f"Produto '{nome}' (ID {produto_id}) excluído. "
                f"Saldo: {saldo} {unidade}. "
                f"Movimentação de exclusão: {exclusao_mov_id}. "
                f"Lotes removidos: {lotes_removidos}. "
                f"Atividades preservadas/desvinculadas: "
                f"{atividades_desvinculadas}. "
                f"Recursos de aulas preservados/desvinculados: "
                f"{recursos_desvinculados}."
            )

            cursor.execute("""
                INSERT INTO logs_auditoria (
                    usuario_id,
                    data_hora,
                    modulo,
                    acao,
                    entidade,
                    registro_id,
                    resultado,
                    detalhes_resumidos
                )
                VALUES (
                    %s, NOW(), 'estoque',
                    'excluir_produto', 'produtos',
                    %s, 'sucesso', %s
                )
            """, (excluido_por, produto_id, detalhes))

        conexao.commit()
        return True

    except Exception as erro:
        conexao.rollback()

        if isinstance(erro, InventoryRepositoryError):
            raise

        raise InventoryRepositoryError(
            f"Falha SQL ao excluir o produto: {erro}"
        ) from erro
'''


# 1. Atualiza o repositório.
replace_between(
    "app/repositories/inventory_repository.py",
    "def excluir_produto(produto_id, excluido_por):",
    "\n\n# ============================================================\n# LOTES",
    replacement
)


# 2. Atualiza o tratamento de erro do service.
service_path = ROOT / "app/inventory/service.py"
s = service_path.read_text(encoding="utf-8")

fn_start = s.find(
    "def excluir_produto(produto_id, excluido_por):"
)
fn_end = s.find(
    "\n\n# ============================================================\n# LOTES",
    fn_start
)

if fn_start < 0 or fn_end < 0:
    raise RuntimeError(
        "Função de exclusão não encontrada em service.py."
    )

fn = s[fn_start:fn_end]

old = '''    except Exception as erro:
        _tratar_erro_repositorio(erro)

    if not excluido:'''

new = '''    except Exception as erro:
        raise InventoryServiceError(
            f"Não foi possível excluir o produto: {erro}"
        ) from erro

    if not excluido:'''

if old not in fn:
    raise RuntimeError(
        "Tratamento esperado não encontrado dentro de excluir_produto."
    )

fn = fn.replace(old, new, 1)

service_path.write_text(
    s[:fn_start] + fn + s[fn_end:],
    encoding="utf-8"
)


# 3. Corrige as mensagens de confirmação no JavaScript.
js_path = ROOT / "app/static/js/inventory-product-detail.js"
js = js_path.read_text(encoding="utf-8")

js = js.replace(
    '''"Todos os registros vinculados a este produto também serão " +
            "removidos, incluindo lotes, movimentações, registros de " +
            "atividades e recursos de aulas.\\n\\n" +
            "O registro da exclusão permanecerá no histórico de auditoria.\\n\\n" +''',
    '''"O cadastro e os lotes serão removidos. As movimentações históricas, " +
            "atividades e recursos de aulas serão preservados, removendo " +
            "apenas os vínculos com o produto.\\n\\n" +
            "A exclusão será registrada na auditoria.\\n\\n" +'''
)

js = js.replace(
    '"Removendo o produto e seus registros relacionados..."',
    '"Excluindo o cadastro e preservando os históricos..."'
)

js_path.write_text(js, encoding="utf-8")


# 4. Corrige as mensagens na tela de detalhes.
html_path = ROOT / "app/templates/inventory/product_detail.html"
h = html_path.read_text(encoding="utf-8")

h = h.replace(
    '''Quantidade de registros relacionados ao produto.
                Eles serão removidos junto com a exclusão definitiva.''',
    '''Quantidade de registros relacionados ao produto.
                Os históricos serão preservados; apenas os vínculos serão removidos.'''
)

h = h.replace(
    '''A exclusão remove permanentemente o cadastro e os
                    registros vinculados, incluindo lotes, movimentações,
                    registros de atividades e recursos de aulas.
                    O evento de exclusão será preservado no histórico
                    de auditoria, com o responsável e a data e hora.
                    Se o produto apenas não estiver mais em uso,
                    utilize a opção de inativação.''',
    '''A exclusão remove permanentemente o cadastro e seus lotes.
                    As movimentações históricas, atividades e recursos de aulas
                    serão preservados, removendo apenas os vínculos com o produto.
                    A operação será registrada na auditoria, com responsável,
                    data e saldo no momento da exclusão. Se o produto apenas
                    não estiver mais em uso, utilize a opção de inativação.'''
)

html_path.write_text(h, encoding="utf-8")


print("Correção aplicada nos quatro arquivos.")
print("Revise com: git diff")
print("Teste primeiro em ambiente de desenvolvimento.")