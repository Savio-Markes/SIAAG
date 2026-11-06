
# Desenvolvido por: Fábio Barbosa

from flask import (
    Blueprint,
    request,
    jsonify,
    session
)

from app.permissions import permission_required
from app.animals import service as animal_service


animals_bp = Blueprint("animals", __name__, url_prefix="/animais")


@animals_bp.route("/", methods=["GET"])
@permission_required("animais.visualizar")
def listar():
    """Lista animais com filtros e paginação."""

    try:
        filtros = {
            "identificacao": request.args.get("identificacao", "").strip(),
            "especie": request.args.get("especie", "").strip(),
            "situacao": request.args.get("situacao", "").strip()
        }

        limite = int(request.args.get("limite", 50))
        deslocamento = int(request.args.get("deslocamento", 0))

        animais = animal_service.listar_animais(
            filtros=filtros,
            limite=limite,
            deslocamento=deslocamento
        )

        return jsonify({
            "sucesso": True,
            "dados": animais
        }), 200

    except ValueError:
        return jsonify({
            "sucesso": False,
            "mensagem": "Parâmetros de paginação inválidos."
        }), 400

    except animal_service.AnimalServiceError as erro:
        return jsonify({
            "sucesso": False,
            "mensagem": str(erro)
        }), 400


@animals_bp.route("/<int:animal_id>", methods=["GET"])
@permission_required("animais.visualizar")
def consultar(animal_id):
    """Consulta os dados de um animal."""

    try:
        animal = animal_service.buscar_animal(animal_id)

        return jsonify({
            "sucesso": True,
            "dados": animal
        }), 200

    except animal_service.AnimalServiceError as erro:
        return jsonify({
            "sucesso": False,
            "mensagem": str(erro)
        }), 404


@animals_bp.route("/", methods=["POST"])
@permission_required("animais.criar")
def cadastrar():
    """Cadastra um novo animal."""

    dados = request.get_json(silent=True)

    if not isinstance(dados, dict):
        return jsonify({
            "sucesso": False,
            "mensagem": "Envie os dados do animal em formato JSON."
        }), 400

    try:
        animal_id = animal_service.cadastrar_animal(
            dados=dados,
            criado_por=session["usuario_id"]
        )

        return jsonify({
            "sucesso": True,
            "mensagem": "Animal cadastrado com sucesso.",
            "animal_id": animal_id
        }), 201

    except animal_service.AnimalServiceError as erro:
        return jsonify({
            "sucesso": False,
            "mensagem": str(erro)
        }), 400


@animals_bp.route("/<int:animal_id>", methods=["PUT"])
@permission_required("animais.editar")
def editar(animal_id):
    """Atualiza os dados cadastrais de um animal."""

    dados = request.get_json(silent=True)

    if not isinstance(dados, dict):
        return jsonify({
            "sucesso": False,
            "mensagem": "Envie os dados em formato JSON."
        }), 400

    try:
        animal_service.editar_animal(animal_id, dados)

        return jsonify({
            "sucesso": True,
            "mensagem": "Animal atualizado com sucesso."
        }), 200

    except animal_service.AnimalServiceError as erro:
        status = 404 if str(erro) == "Animal não encontrado." else 400

        return jsonify({
            "sucesso": False,
            "mensagem": str(erro)
        }), status


@animals_bp.route("/<int:animal_id>/inativar", methods=["POST"])
@permission_required("animais.editar")
def inativar(animal_id):
    """Inativa um animal sem excluir seu histórico."""

    try:
        animal_service.inativar_animal(animal_id)

        return jsonify({
            "sucesso": True,
            "mensagem": "Animal inativado com sucesso."
        }), 200

    except animal_service.AnimalServiceError as erro:
        status = 404 if str(erro) == "Animal não encontrado." else 400

        return jsonify({
            "sucesso": False,
            "mensagem": str(erro)
        }), status
