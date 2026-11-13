
# Desenvolvido por: Fábio Barbosa

from app import create_app, permissions
from app.animals import service as animal_service


def preparar_cliente(monkeypatch, autorizado=True):
    """Prepara cliente autenticado para testar o módulo de animais."""

    app = create_app()
    app.config["TESTING"] = True

    monkeypatch.setattr(
        permissions,
        "verificar_permissao_usuario",
        lambda usuario_id, codigo: autorizado
    )

    cliente = app.test_client()

    with cliente.session_transaction() as sessao:
        sessao["usuario_id"] = 1
        sessao["usuario_nome"] = "Usuário de teste"

    return cliente


# ==================================================
# TESTES DAS ROTAS DE ANIMAIS
# ==================================================

def test_listar_animais_com_filtro_identificacao(monkeypatch):
    """Verifica se a listagem recebe o filtro de identificação."""

    dados = [{"id": 1, "identificacao": "BRINCO-001"}]

    def listar(filtros, limite, deslocamento):
        assert filtros["identificacao"] == "BRINCO-001"
        return dados

    monkeypatch.setattr(
        animal_service,
        "listar_animais",
        listar
    )

    cliente = preparar_cliente(monkeypatch)

    resposta = cliente.get(
        "/animais/?identificacao=BRINCO-001"
    )

    assert resposta.status_code == 200
    assert resposta.json["dados"] == dados


def test_listar_animais_com_paginacao_invalida(monkeypatch):
    """Verifica o tratamento de parâmetros inválidos."""

    cliente = preparar_cliente(monkeypatch)

    resposta = cliente.get("/animais/?limite=abc")

    assert resposta.status_code == 400
    assert resposta.json["sucesso"] is False


def test_listar_animais_sem_permissao(monkeypatch):
    """Verifica o bloqueio de usuário sem autorização."""

    cliente = preparar_cliente(monkeypatch, autorizado=False)

    resposta = cliente.get("/animais/")

    assert resposta.status_code == 403


def test_cadastrar_animal_com_sucesso(monkeypatch):
    """Verifica o cadastro de um animal."""

    monkeypatch.setattr(
        animal_service,
        "cadastrar_animal",
        lambda dados, criado_por: 10
    )

    cliente = preparar_cliente(monkeypatch)

    resposta = cliente.post(
        "/animais/",
        json={
            "identificacao": "BRINCO-010",
            "especie": "Bovino",
            "situacao": "Ativo"
        }
    )

    assert resposta.status_code == 201
    assert resposta.json["animal_id"] == 10


def test_cadastrar_animal_sem_json(monkeypatch):
    """Verifica a rejeição de requisição sem JSON válido."""

    cliente = preparar_cliente(monkeypatch)

    resposta = cliente.post(
        "/animais/",
        data="dados inválidos",
        content_type="text/plain"
    )

    assert resposta.status_code == 400


def test_consultar_animal_inexistente(monkeypatch):
    """Verifica o retorno para animal não encontrado."""

    def buscar(animal_id):
        raise animal_service.AnimalServiceError(
            "Animal não encontrado."
        )

    monkeypatch.setattr(
        animal_service,
        "buscar_animal",
        buscar
    )

    cliente = preparar_cliente(monkeypatch)

    resposta = cliente.get("/animais/999")

    assert resposta.status_code == 404


def test_bloquear_identificacao_duplicada(monkeypatch):
    """Verifica a regra de identificação única no Service."""

    monkeypatch.setattr(
        animal_service.animal_repository,
        "buscar_animal_por_identificacao",
        lambda identificacao: {
            "id": 5,
            "identificacao": identificacao
        }
    )

    try:
        animal_service.validar_identificacao_unica(
            "BRINCO-005"
        )
        assert False, "Deveria bloquear a identificação duplicada."

    except animal_service.AnimalServiceError as erro:
        assert "identificação" in str(erro)


def test_permitir_identificacao_do_proprio_animal(monkeypatch):
    """Permite manter a identificação do próprio registro."""

    monkeypatch.setattr(
        animal_service.animal_repository,
        "buscar_animal_por_identificacao",
        lambda identificacao: {
            "id": 5,
            "identificacao": identificacao
        }
    )

    animal_service.validar_identificacao_unica(
        "BRINCO-005",
        animal_id=5
    )


# ==================================================
# TESTES DE EDIÇÃO E INATIVAÇÃO
# ==================================================

def test_editar_animal_com_sucesso(monkeypatch):
    """Verifica a edição de um animal."""

    monkeypatch.setattr(
        animal_service,
        "editar_animal",
        lambda animal_id, dados: None
    )

    cliente = preparar_cliente(monkeypatch)

    resposta = cliente.put(
        "/animais/10",
        json={
            "identificacao": "BRINCO-010",
            "especie": "Bovino",
            "situacao": "Ativo"
        }
    )

    assert resposta.status_code == 200
    assert resposta.json["sucesso"] is True


def test_editar_animal_sem_json(monkeypatch):
    """Verifica a rejeição de edição sem JSON."""

    cliente = preparar_cliente(monkeypatch)

    resposta = cliente.put(
        "/animais/10",
        data="dados inválidos",
        content_type="text/plain"
    )

    assert resposta.status_code == 400


def test_editar_animal_inexistente(monkeypatch):
    """Verifica o retorno para animal inexistente."""

    def editar(animal_id, dados):
        raise animal_service.AnimalServiceError(
            "Animal não encontrado."
        )

    monkeypatch.setattr(
        animal_service,
        "editar_animal",
        editar
    )

    cliente = preparar_cliente(monkeypatch)

    resposta = cliente.put(
        "/animais/999",
        json={"situacao": "Ativo"}
    )

    assert resposta.status_code == 404


def test_editar_animal_sem_permissao(monkeypatch):
    """Verifica o bloqueio de edição sem autorização."""

    cliente = preparar_cliente(monkeypatch, autorizado=False)

    resposta = cliente.put(
        "/animais/10",
        json={"situacao": "Ativo"}
    )

    assert resposta.status_code == 403


def test_inativar_animal_com_sucesso(monkeypatch):
    """Verifica a inativação de um animal."""

    monkeypatch.setattr(
        animal_service,
        "inativar_animal",
        lambda animal_id: None
    )

    cliente = preparar_cliente(monkeypatch)

    resposta = cliente.post("/animais/10/inativar")

    assert resposta.status_code == 200
    assert resposta.json["sucesso"] is True


def test_inativar_animal_sem_permissao(monkeypatch):
    """Verifica o bloqueio de inativação sem autorização."""

    cliente = preparar_cliente(monkeypatch, autorizado=False)

    resposta = cliente.post("/animais/10/inativar")

    assert resposta.status_code == 403


# ==================================================
# TESTES DIRETOS DO SERVICE
# ==================================================

def test_service_rejeita_identificacao_obrigatoria():
    """Impede cadastro sem identificação."""

    try:
        animal_service.validar_dados_animal({
            "especie": "Bovino",
            "situacao": "Ativo"
        })
        assert False, "Deveria exigir identificação."

    except animal_service.AnimalServiceError as erro:
        assert "identificacao" in str(erro)


def test_service_rejeita_especie_obrigatoria():
    """Impede cadastro sem espécie."""

    try:
        animal_service.validar_dados_animal({
            "identificacao": "BRINCO-020",
            "situacao": "Ativo"
        })
        assert False, "Deveria exigir espécie."

    except animal_service.AnimalServiceError as erro:
        assert "especie" in str(erro)


def test_service_rejeita_data_nascimento_invalida():
    """Valida o formato da data de nascimento."""

    try:
        animal_service.validar_dados_animal({
            "identificacao": "BRINCO-021",
            "especie": "Bovino",
            "situacao": "Ativo",
            "nascimento": "32/15/2026"
        })
        assert False, "Deveria rejeitar a data."

    except animal_service.AnimalServiceError as erro:
        assert "nascimento" in str(erro)


def test_service_rejeita_data_entrada_invalida():
    """Valida o formato da data de entrada."""

    try:
        animal_service.validar_dados_animal({
            "identificacao": "BRINCO-022",
            "especie": "Bovino",
            "situacao": "Ativo",
            "data_entrada": "data-invalida"
        })
        assert False, "Deveria rejeitar a data."

    except animal_service.AnimalServiceError as erro:
        assert "entrada" in str(erro)


def test_service_rejeita_ativo_invalido():
    """Impede valores inválidos no campo ativo."""

    try:
        animal_service.validar_dados_animal({
            "identificacao": "BRINCO-023",
            "especie": "Bovino",
            "situacao": "Ativo",
            "ativo": 5
        })
        assert False, "Deveria rejeitar o estado."

    except animal_service.AnimalServiceError as erro:
        assert "atividade" in str(erro)


def test_service_rejeita_limite_acima_do_maximo(monkeypatch):
    """Limita consultas a no máximo 100 registros."""

    try:
        animal_service.listar_animais(limite=101)
        assert False, "Deveria rejeitar o limite."

    except animal_service.AnimalServiceError as erro:
        assert "Limite" in str(erro)


def test_service_rejeita_deslocamento_negativo():
    """Impede paginação com deslocamento negativo."""

    try:
        animal_service.listar_animais(deslocamento=-1)
        assert False, "Deveria rejeitar o deslocamento."

    except animal_service.AnimalServiceError as erro:
        assert "Deslocamento" in str(erro)


def test_service_rejeita_identificacao_vazia_na_edicao():
    """Impede apagar a identificação durante a edição."""

    try:
        animal_service.validar_dados_animal(
            {"identificacao": "   "},
            atualizacao=True
        )
        assert False, "Deveria rejeitar identificação vazia."

    except animal_service.AnimalServiceError as erro:
        assert "identificacao" in str(erro)
