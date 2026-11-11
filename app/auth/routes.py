
# Desenvolvido por: Fábio Barbosa

from flask import (
    Blueprint,
    render_template,
    request,
    session,
    flash,
    redirect,
    url_for
)

from app.auth.service import autenticar_usuario


auth_bp = Blueprint("auth", __name__)


# Rotas responsáveis pela autenticação dos usuários.

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Exibe a tela de login e processa a autenticação."""

    if request.method == "POST":
        login_usuario = request.form.get("login", "").strip()
        senha = request.form.get("senha", "")

        usuario = autenticar_usuario(login_usuario, senha)

        if usuario:
            session.clear()
            session["usuario_id"] = usuario["id"]
            session["usuario_nome"] = usuario["nome"]

            return redirect(url_for("dashboard.index"))

        flash("Login ou senha inválidos.", "erro")

    return render_template("auth/login.html")


@auth_bp.route("/logout", methods=["POST"])
def logout():
    """Encerra a sessão do usuário autenticado."""

    session.clear()

    flash("Sessão encerrada com sucesso.", "sucesso")

    return redirect(url_for("auth.login"))
