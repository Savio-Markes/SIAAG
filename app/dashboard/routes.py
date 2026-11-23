# Desenvolvido por: Fábio Barbosa

from flask import Blueprint, render_template

from app.decorators import login_required
from app.permissions import possui_permissao

from app.dashboard.service import (
    obter_dados_dashboard,
    obter_dados_estoque_dashboard,
)


dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
@login_required
def index():
    """Exibe o painel principal do SIAAG."""

    pode_visualizar_animais = possui_permissao(
        "animais.visualizar"
    )

    pode_visualizar_estoque = possui_permissao(
        "estoque.visualizar"
    )

    dashboard = {
        "pode_visualizar_animais": pode_visualizar_animais,
        "pode_visualizar_estoque": pode_visualizar_estoque,

        # Indicadores de animais
        "total_animais": None,
        "animais_ativos": None,
        "animais_inativos": None,
        "especies": [],
        "situacoes": [],

        # Indicadores de estoque
        "total_produtos": None,
        "produtos_ativos": None,
        "produtos_inativos": None,
        "estoque_baixo": None,
        "categorias_estoque": [],
        "movimentacoes_estoque": {
            "entrada": 0,
            "saida": 0,
            "ajuste": 0,
        },
        "total_movimentacoes": 0,
    }

    if pode_visualizar_animais:
        dashboard.update(obter_dados_dashboard())

    if pode_visualizar_estoque:
        dashboard.update(obter_dados_estoque_dashboard())

    return render_template(
        "dashboard/index.html",
        dashboard=dashboard,
    )