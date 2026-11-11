
# Desenvolvido por: Fábio Barbosa

from functools import wraps
from flask import session, redirect, url_for, flash


# Proteção de acesso às rotas internas.

def login_required(func):
    """Exige uma sessão autenticada para acessar a rota."""

    @wraps(func)
    def decorated_view(*args, **kwargs):

        if "usuario_id" not in session:
            flash("Faça login para acessar o sistema.", "erro")
            return redirect(url_for("auth.login"))

        return func(*args, **kwargs)

    return decorated_view
