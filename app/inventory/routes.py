
# Desenvolvido por: Fábio Barbosa

from collections import Counter

from flask import (
    Blueprint, render_template, request, redirect,
    url_for, flash, session, jsonify
)

from app.permissions import permission_required
from app.inventory import service


inventory_bp = Blueprint(
    "inventory", __name__, url_prefix="/estoque"
)


# ============================================================
# ESTOQUE - PAINEL PRINCIPAL
# ============================================================

@inventory_bp.route("/")
@permission_required("estoque.visualizar")
def index():
    filtros = {}

    busca = request.args.get("busca", "").strip()
    categoria_id = request.args.get("categoria_id", "").strip()
    ativo = request.args.get("ativo", "").strip()

    if busca:
        filtros["busca"] = busca
    if categoria_id:
        filtros["categoria_id"] = categoria_id
    if ativo in ("0", "1"):
        filtros["ativo"] = ativo

    produtos = service.listar_produtos(filtros=filtros, limite=100)

    total_produtos = service.contar_produtos()
    produtos_ativos = service.contar_produtos({"ativo": 1})
    produtos_inativos = service.contar_produtos({"ativo": 0})

    produtos_estoque_ativo = service.listar_produtos(
        filtros={"ativo": 1}, limite=100
    )

    estoque_baixo = sum(
        1 for produto in produtos_estoque_ativo
        if produto["quantidade_atual"] is not None
        and produto["quantidade_atual"] <= produto["estoque_minimo"]
    )

    categorias = service.listar_categorias()

    total_entradas = service.contar_movimentacoes(tipo="entrada")
    total_saidas = service.contar_movimentacoes(tipo="saida")
    total_ajustes = service.contar_movimentacoes(tipo="ajuste")
    total_movimentacoes = total_entradas + total_saidas + total_ajustes

    distribuicao = Counter(
        produto.get("categoria_nome") or "Sem categoria"
        for produto in produtos
    )

    categorias_grafico = [
        {"nome": nome, "total": total}
        for nome, total in distribuicao.most_common(6)
    ]

    return render_template(
        "inventory/list.html",
        produtos=produtos,
        categorias=categorias,
        filtros=filtros,
        total_produtos=total_produtos,
        produtos_ativos=produtos_ativos,
        produtos_inativos=produtos_inativos,
        estoque_baixo=estoque_baixo,
        total_entradas=total_entradas,
        total_saidas=total_saidas,
        total_ajustes=total_ajustes,
        total_movimentacoes=total_movimentacoes,
        categorias_grafico=categorias_grafico
    )


# ============================================================
# PRODUTOS
# ============================================================

@inventory_bp.route("/produtos/novo", methods=["GET", "POST"])
@permission_required("estoque.criar_produto")
def novo_produto():

    if request.method == "POST":
        dados = request.form.to_dict()
        dados.pop("ativo", None)

        try:
            service.cadastrar_produto(
                dados=dados,
                criado_por=session["usuario_id"]
            )
            flash("Produto cadastrado com sucesso!", "sucesso")
            return redirect(url_for("inventory.index"))

        except service.InventoryServiceError as erro:
            flash(str(erro), "erro")
        except Exception:
            flash("Ocorreu um erro ao cadastrar o produto.", "erro")

    categorias = service.listar_categorias()

    return render_template(
        "inventory/product_form.html",
        categorias=categorias,
        editando=False
    )


@inventory_bp.route(
    "/produtos/<int:produto_id>/editar",
    methods=["GET", "POST"]
)
@permission_required("estoque.criar_produto")
def editar_produto(produto_id):

    try:
        produto = service.buscar_produto(produto_id)

        if request.method == "POST":
            dados = request.form.to_dict()
            dados.pop("ativo", None)

            dados["controla_lote_validade"] = (
                "1" if "controla_lote_validade" in request.form else "0"
            )

            service.editar_produto(produto_id, dados)
            flash("Produto atualizado com sucesso!", "sucesso")
            return redirect(url_for("inventory.index"))

        categorias = service.listar_categorias()

        return render_template(
            "inventory/product_form.html",
            produto=produto,
            categorias=categorias,
            editando=True
        )

    except service.InventoryServiceError as erro:
        flash(str(erro), "erro")
        return redirect(url_for("inventory.index"))


# ============================================================
# LOTES
# ============================================================

@inventory_bp.route("/produtos/<int:produto_id>/lotes", methods=["GET"])
@permission_required("estoque.visualizar")
def listar_lotes(produto_id):

    try:
        produto = service.buscar_produto(produto_id)

        if int(produto["controla_lote_validade"]) != 1:
            flash("Este produto não utiliza controle de lote.", "erro")
            return redirect(url_for("inventory.index"))

        lotes = service.listar_lotes_produto(produto_id)

        return render_template(
            "inventory/lotes.html",
            produto=produto,
            lotes=lotes
        )

    except service.InventoryServiceError as erro:
        flash(str(erro), "erro")
        return redirect(url_for("inventory.index"))


@inventory_bp.route(
    "/produtos/<int:produto_id>/lotes",
    methods=["POST"]
)
@permission_required("estoque.movimentar")
def cadastrar_lote(produto_id):

    dados = request.get_json(silent=True)
    envio_por_formulario = dados is None

    if envio_por_formulario:
        dados = request.form.to_dict()

    dados["produto_id"] = produto_id
    responsavel_id = session.get("usuario_id")

    try:
        resultado = service.cadastrar_lote(
            dados=dados,
            responsavel_id=responsavel_id
        )

        if isinstance(resultado, dict):
            lote_id = resultado["lote_id"]
            movimentacao_id = resultado.get("movimentacao_id")
        else:
            lote_id = resultado
            movimentacao_id = None

        if envio_por_formulario:
            flash(
                "Lote cadastrado e entrada inicial registrada com sucesso!",
                "sucesso"
            )
            return redirect(
                url_for("inventory.listar_lotes", produto_id=produto_id)
            )

        return jsonify({
            "sucesso": True,
            "mensagem": "Lote cadastrado com sucesso.",
            "lote_id": lote_id,
            "movimentacao_id": movimentacao_id
        }), 201

    except service.InventoryServiceError as erro:

        if envio_por_formulario:
            flash(str(erro), "erro")
            return redirect(
                url_for("inventory.listar_lotes", produto_id=produto_id)
            )

        return jsonify({
            "sucesso": False,
            "mensagem": str(erro)
        }), 400

    except Exception:

        if envio_por_formulario:
            flash("Erro ao cadastrar o lote.", "erro")
            return redirect(
                url_for("inventory.listar_lotes", produto_id=produto_id)
            )

        return jsonify({
            "sucesso": False,
            "mensagem": "Erro ao cadastrar o lote."
        }), 500


# ============================================================
# MOVIMENTAÇÕES
# ============================================================

@inventory_bp.route("/movimentacoes")
@permission_required("estoque.visualizar")
def movimentacoes():

    produto_id = request.args.get("produto_id", type=int)
    tipo = request.args.get("tipo", "").strip()

    try:
        movimentacoes = service.listar_movimentacoes(
            produto_id=produto_id,
            tipo=tipo or None,
            limite=100
        )

        return render_template(
            "inventory/movements.html",
            movimentacoes=movimentacoes
        )

    except service.InventoryServiceError as erro:
        flash(str(erro), "erro")
        return redirect(url_for("inventory.index"))


@inventory_bp.route(
    "/movimentacoes/nova",
    methods=["GET", "POST"]
)
@permission_required("estoque.movimentar")
def nova_movimentacao():

    if request.method == "POST":
        dados = request.form.to_dict()
        dados.pop("responsavel_id", None)

        try:
            service.registrar_movimentacao(
                dados=dados,
                responsavel_id=session["usuario_id"]
            )
            flash("Movimentação registrada com sucesso!", "sucesso")
            return redirect(url_for("inventory.movimentacoes"))

        except service.InventoryServiceError as erro:
            flash(str(erro), "erro")
        except Exception:
            flash(
                "Ocorreu um erro ao registrar a movimentação.",
                "erro"
            )

    produtos = service.listar_produtos(
        filtros={"ativo": 1}, limite=100
    )

    lotes = []

    for produto in produtos:
        if int(produto["controla_lote_validade"]) == 1:
            lotes.extend(
                service.listar_lotes_produto(produto["id"])
            )

    return render_template(
        "inventory/movement_form.html",
        produtos=produtos,
        lotes=lotes
    )


# ============================================================
# ATIVAÇÃO E INATIVAÇÃO
# ============================================================

@inventory_bp.route(
    "/produtos/<int:produto_id>/inativar",
    methods=["POST"]
)
@permission_required("estoque.criar_produto")
def inativar_produto(produto_id):

    try:
        service.inativar_produto(produto_id)
        flash("Produto inativado com sucesso.", "sucesso")
    except service.InventoryServiceError as erro:
        flash(str(erro), "erro")
    except Exception:
        flash("Não foi possível inativar o produto.", "erro")

    return redirect(url_for("inventory.index"))


@inventory_bp.route(
    "/produtos/<int:produto_id>/reativar",
    methods=["POST"]
)
@permission_required("estoque.criar_produto")
def reativar_produto(produto_id):

    try:
        service.reativar_produto(produto_id)
        flash("Produto reativado com sucesso.", "sucesso")
    except service.InventoryServiceError as erro:
        flash(str(erro), "erro")
    except Exception:
        flash("Não foi possível reativar o produto.", "erro")

    return redirect(url_for("inventory.index"))
