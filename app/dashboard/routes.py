
# Desenvolvido por: Fábio Barbosa

from flask import Blueprint, render_template

from app.decorators import login_required
from app.permissions import possui_permissao
from app.dashboard.service import obter_dados_dashboard


dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
@login_required
def index():
    """Exibe o painel principal do SIAAG."""

    pode_visualizar_animais = possui_permissao(
        "animais.visualizar"
    )

    dashboard = {
        "pode_visualizar_animais": pode_visualizar_animais,
        "total_animais": None,
        "animais_ativos": None,
        "animais_inativos": None,
        "especies": [],
        "situacoes": [],
    }

    if pode_visualizar_animais:
        dashboard.update(obter_dados_dashboard())

    return render_template(
        "dashboard/index.html",
        dashboard=dashboard,
    )
