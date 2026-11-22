# Desenvolvido por: Fábio Barbosa

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    jsonify
)

from app.permissions import permission_required
from app.inventory import service


inventory_bp = Blueprint(
    "inventory",
    __name__,
    url_prefix="/estoque"
)


# ============================================================
# ESTOQUE - DASHBOARD
# ============================================================

@inventory_bp.route("/")
@permission_required("estoque.visualizar")
def index():
    """Exibe a listagem principal do estoque."""

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

    produtos = service.listar_produtos(
        filtros=filtros,
        limite=100
    )

    total_produtos = service.contar_produtos()

    produtos_ativos = service.contar_produtos(
        {"ativo": 1}
    )

    produtos_estoque_ativo = service.listar_produtos(
        filtros={"ativo": 1},
        limite=100
    )

    estoque_baixo = sum(
        1
        for produto in produtos_estoque_ativo
        if produto["quantidade_atual"] is not None
        and produto["quantidade_atual"] <= produto["estoque_minimo"]
    )

    categorias = service.listar_categorias()

    return render_template(
        "inventory/list.html",
        produtos=produtos,
        categorias=categorias,
        total_produtos=total_produtos,
        produtos_ativos=produtos_ativos,
        estoque_baixo=estoque_baixo
    )


# ============================================================
# PRODUTOS
# ============================================================

@inventory_bp.route("/produtos/novo", methods=["GET", "POST"])
@permission_required("estoque.criar_produto")
def novo_produto():
    """Exibe o formulário e realiza o cadastro de produtos."""

    if request.method == "POST":

        dados = request.form.to_dict()
        dados.pop("ativo", None)

        try:
            service.cadastrar_produto(
                dados=dados,
                criado_por=session["usuario_id"]
            )

            flash(
                "Produto cadastrado com sucesso!",
                "sucesso"
            )

            return redirect(
                url_for("inventory.index")
            )

        except service.InventoryServiceError as erro:
            flash(str(erro), "erro")

        except Exception:
            flash(
                "Ocorreu um erro ao cadastrar o produto.",
                "erro"
            )

    categorias = service.listar_categorias()

    return render_template(
        "inventory/product_form.html",
        categorias=categorias
    )


# ============================================================
# LOTES
# ============================================================

@inventory_bp.route(
    "/produtos/<int:produto_id>/lotes",
    methods=["POST"]
)
@permission_required("estoque.movimentar")
def cadastrar_lote(produto_id):
    """Cadastra um lote e registra sua entrada inicial."""

    dados = request.get_json(silent=True)

    if dados is None:
        dados = request.form.to_dict()

    dados["produto_id"] = produto_id

    responsavel_id = session.get("usuario_id")

    try:
        resultado = service.cadastrar_lote(
            dados=dados,
            responsavel_id=responsavel_id
        )

        # O service retorna os identificadores do lote
        # e da movimentação inicial.
        if isinstance(resultado, dict):
            lote_id = resultado["lote_id"]
            movimentacao_id = resultado.get("movimentacao_id")
        else:
            lote_id = resultado
            movimentacao_id = None

        return jsonify({
            "sucesso": True,
            "mensagem": "Lote cadastrado com sucesso.",
            "lote_id": lote_id,
            "movimentacao_id": movimentacao_id
        }), 201

    except service.InventoryServiceError as erro:
        return jsonify({
            "sucesso": False,
            "mensagem": str(erro)
        }), 400

    except Exception:
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
    """Exibe o histórico de movimentações."""

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

        return redirect(
            url_for("inventory.index")
        )


@inventory_bp.route(
    "/movimentacoes/nova",
    methods=["GET", "POST"]
)
@permission_required("estoque.movimentar")
def nova_movimentacao():
    """Exibe o formulário e registra entradas, saídas e ajustes."""

    if request.method == "POST":

        dados = request.form.to_dict()

        # O responsável é sempre obtido da sessão autenticada.
        dados.pop("responsavel_id", None)

        try:
            service.registrar_movimentacao(
                dados=dados,
                responsavel_id=session["usuario_id"]
            )

            flash(
                "Movimentação registrada com sucesso!",
                "sucesso"
            )

            return redirect(
                url_for("inventory.movimentacoes")
            )

        except service.InventoryServiceError as erro:
            flash(str(erro), "erro")

        except Exception:
            flash(
                "Ocorreu um erro ao registrar a movimentação.",
                "erro"
            )

    produtos = service.listar_produtos(
        filtros={"ativo": 1},
        limite=100
    )

    lotes = []

    for produto in produtos:
        if int(produto["controla_lote_validade"]) == 1:
            lotes_produto = service.listar_lotes_produto(
                produto["id"]
            )

            lotes.extend(lotes_produto)

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
    """Inativa um produto sem excluir seu histórico."""

    try:
        service.inativar_produto(produto_id)

        flash(
            "Produto inativado com sucesso.",
            "sucesso"
        )

    except service.InventoryServiceError as erro:
        flash(str(erro), "erro")

    except Exception:
        flash(
            "Não foi possível inativar o produto.",
            "erro"
        )

    return redirect(
        url_for("inventory.index")
    )


@inventory_bp.route(
    "/produtos/<int:produto_id>/reativar",
    methods=["POST"]
)
@permission_required("estoque.criar_produto")
def reativar_produto(produto_id):
    """Reativa um produto anteriormente inativado."""

    try:
        service.reativar_produto(produto_id)

        flash(
            "Produto reativado com sucesso.",
            "sucesso"
        )

    except service.InventoryServiceError as erro:
        flash(str(erro), "erro")

    except Exception:
        flash(
            "Não foi possível reativar o produto.",
            "erro"
        )

    return redirect(
        url_for("inventory.index")
    )