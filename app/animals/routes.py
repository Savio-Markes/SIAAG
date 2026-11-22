# Desenvolvido por: Fábio Barbosa

from flask import (
    Blueprint,
    request,
    jsonify,
    session,
    render_template,
    abort
)

from app.permissions import permission_required
from app.animals import service as animal_service


animals_bp = Blueprint("animals", __name__, url_prefix="/animais")


@animals_bp.route("/painel", methods=["GET"])
@permission_required("animais.visualizar")
def painel():
    return render_template("animals/index.html")


@animals_bp.route("/novo", methods=["GET"])
@permission_required("animais.criar")
def novo():
    return render_template("animals/form.html")


@animals_bp.route("/<int:animal_id>/painel", methods=["GET"])
@permission_required("animais.visualizar")
def ficha(animal_id):
    try:
        animal = animal_service.buscar_animal(animal_id)
        return render_template("animals/detail.html", animal=animal)
    except animal_service.AnimalServiceError:
        abort(404)


@animals_bp.route("/<int:animal_id>/editar", methods=["GET"])
@permission_required("animais.editar")
def editar_pagina(animal_id):
    try:
        animal = animal_service.buscar_animal(animal_id)
        return render_template("animals/edit.html", animal=animal)
    except animal_service.AnimalServiceError:
        abort(404)


@animals_bp.route("/", methods=["GET"])
@permission_required("animais.visualizar")
def listar():
    try:
        filtros = {
            "identificacao": request.args.get(
                "identificacao", ""
            ).strip(),
            "especie": request.args.get("especie", "").strip(),
            "situacao": request.args.get("situacao", "").strip()
        }

        ativo = request.args.get("ativo")

        if ativo in ("0", "1"):
            filtros["ativo"] = int(ativo)
        elif ativo not in (None, ""):
            return jsonify({
                "sucesso": False,
                "mensagem": "Filtro de atividade inválido."
            }), 400

        limite = int(request.args.get("limite", 50))
        deslocamento = int(request.args.get("deslocamento", 0))

        animais = animal_service.listar_animais(
            filtros=filtros,
            limite=limite,
            deslocamento=deslocamento
        )

        total = animal_service.contar_animais(filtros=filtros)

        # Indicadores gerais, independentes dos filtros da tabela.
        indicadores = animal_service.obter_indicadores()

        return jsonify({
            "sucesso": True,
            "dados": animais,
            "total": total,
            "limite": limite,
            "deslocamento": deslocamento,
            "indicadores": indicadores
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
        status = (
            404 if str(erro) == "Animal não encontrado." else 400
        )

        return jsonify({
            "sucesso": False,
            "mensagem": str(erro)
        }), status


@animals_bp.route("/<int:animal_id>/inativar", methods=["POST"])
@permission_required("animais.editar")
def inativar(animal_id):
    try:
        animal_service.inativar_animal(animal_id)

        return jsonify({
            "sucesso": True,
            "mensagem": "Animal inativado com sucesso."
        }), 200

    except animal_service.AnimalServiceError as erro:
        status = (
            404 if str(erro) == "Animal não encontrado." else 400
        )

        return jsonify({
            "sucesso": False,
            "mensagem": str(erro)
        }), status


@animals_bp.route("/<int:animal_id>/reativar", methods=["POST"])
@permission_required("animais.editar")
def reativar(animal_id):
    try:
        animal_service.reativar_animal(animal_id)

        return jsonify({
            "sucesso": True,
            "mensagem": "Animal reativado com sucesso."
        }), 200

    except animal_service.AnimalServiceError as erro:
        status = (
            404 if str(erro) == "Animal não encontrado." else 400
        )

        return jsonify({
            "sucesso": False,
            "mensagem": str(erro)
        }), status


@animals_bp.route("/<int:animal_id>/excluir", methods=["POST"])
@permission_required("animais.editar")
def excluir(animal_id):
    try:
        animal_service.excluir_animal(
            animal_id=animal_id,
            excluido_por=session["usuario_id"]
        )

        return jsonify({
            "sucesso": True,
            "mensagem": "Animal excluído com sucesso."
        }), 200

    except animal_service.AnimalServiceError as erro:
        mensagem = str(erro)

        if mensagem == "Animal não encontrado.":
            status = 404
        elif "histórico vinculado" in mensagem:
            status = 409
        else:
            status = 400

        return jsonify({
            "sucesso": False,
            "mensagem": mensagem
        }), status