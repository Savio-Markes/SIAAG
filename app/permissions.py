# Desenvolvido por: Fábio Barbosa

from functools import wraps

from flask import session, redirect, url_for, flash


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
    """Verifica se a sessão possui determinada permissão."""

    permissoes_usuario = session.get("permissoes", [])

    return codigo in permissoes_usuario


def permission_required(codigo):
    """Protege uma rota conforme a permissão exigida."""

    def decorator(func):
        @wraps(func)
        def decorated_view(*args, **kwargs):

            if "usuario_id" not in session:
                flash(
                    "Faça login para acessar o sistema.",
                    "erro"
                )
                return redirect(url_for("auth.login"))

            if codigo not in PERMISSOES:
                return "Permissão inválida.", 403

            if not possui_permissao(codigo):
                return "Acesso não autorizado.", 403

            return func(*args, **kwargs)

        return decorated_view

    return decorator