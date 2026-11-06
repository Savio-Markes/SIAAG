
# Desenvolvido por: Fábio Barbosa

from functools import wraps

from flask import session, redirect, url_for, flash

from app.auth.permission_service import verificar_permissao_usuario


# Códigos de permissões utilizados pelo SIAAG.

PERMISSOES = {
    "dashboard.visualizar",
    "usuarios.visualizar",
    "usuarios.administrar",
    "animais.visualizar",
    "animais.criar",
    "animais.editar",
    "veterinaria.registrar",
    "veterinaria.consultar_historico",
    "estoque.visualizar",
    "estoque.criar_produto",
    "estoque.movimentar",
    "atividades.visualizar",
    "atividades.registrar",
    "aulas.visualizar",
    "aulas.registrar",
    "pesquisa.visualizar",
    "pesquisa.registrar",
    "patrimonio.visualizar",
    "patrimonio.registrar_manutencao",
    "relatorios.visualizar",
    "auditoria.visualizar"
}


def possui_permissao(codigo):
    """Consulta no banco se o usuário possui determinada permissão."""

    usuario_id = session.get("usuario_id")

    if not usuario_id or codigo not in PERMISSOES:
        return False

    return verificar_permissao_usuario(usuario_id, codigo)


def permission_required(codigo):
    """Protege uma rota conforme a permissão exigida."""

    def decorator(func):
        @wraps(func)
        def decorated_view(*args, **kwargs):

            if "usuario_id" not in session:
                flash("Faça login para acessar o sistema.", "erro")
                return redirect(url_for("auth.login"))

            if not possui_permissao(codigo):
                return "Acesso não autorizado.", 403

            return func(*args, **kwargs)

        return decorated_view

    return decorator
