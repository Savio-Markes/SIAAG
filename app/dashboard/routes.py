
# Desenvolvido por: Fábio Barbosa

from flask import Blueprint, render_template
from app.decorators import login_required


dashboard_bp = Blueprint("dashboard", __name__)


# Rotas principais do painel.

@dashboard_bp.route("/")
@login_required
def index():
    """Exibe o painel principal do SIAAG."""
    return render_template("dashboard/index.html")
