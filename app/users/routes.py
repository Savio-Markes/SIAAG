
# Desenvolvido por: Fábio Barbosa

from flask import Blueprint, jsonify, request, session

from app.permissions import permission_required
from app.auth.permission_service import (
    listar_permissoes_usuario,
    conceder_permissao_usuario,
    revogar_permissao_usuario
)


users_bp = Blueprint("users", __name__, url_prefix="/usuarios")


# Rotas administrativas de gerenciamento de permissões.


@users_bp.route("/<int:usuario_id>/permissoes", methods=["GET"])
@permission_required("usuarios.administrar")
def listar_permissoes(usuario_id):
    """Consulta as permissões concedidas a um usuário."""

    permissoes = listar_permissoes_usuario(usuario_id)

    return jsonify({
        "usuario_id": usuario_id,
        "permissoes": permissoes
    }), 200


@users_bp.route("/<int:usuario_id>/permissoes", methods=["POST"])
@permission_required("usuarios.administrar")
def conceder_permissao(usuario_id):
    """Concede uma permissão ao usuário."""

    dados = request.get_json(silent=True) or {}
    codigo = dados.get("codigo", "").strip()

    if not codigo:
        return jsonify({
            "erro": "Informe o código da permissão."
        }), 400

    resultado = conceder_permissao_usuario(
        usuario_id,
        codigo,
        session["usuario_id"]
    )

    if not resultado:
        return jsonify({
            "erro": "Permissão inválida ou já concedida."
        }), 400

    return jsonify({
        "mensagem": "Permissão concedida com sucesso."
    }), 201


@users_bp.route(
    "/<int:usuario_id>/permissoes/<string:codigo>",
    methods=["DELETE"]
)
@permission_required("usuarios.administrar")
def revogar_permissao(usuario_id, codigo):
    """Revoga uma permissão do usuário."""

    resultado = revogar_permissao_usuario(
        usuario_id,
        codigo,
        session["usuario_id"]
    )

    if not resultado:
        return jsonify({
            "erro": "Permissão não encontrada ou não concedida."
        }), 404

    return jsonify({
        "mensagem": "Permissão revogada com sucesso."
    }), 200
