
# Desenvolvido por: Fábio Barbosa

from app.repositories import animal_repository


class CursorFake:
    """Simula o cursor do banco de dados."""

    def __init__(self):
        self.consulta = None
        self.parametros = None
        self.resultado = None
        self.resultados = []
        self.lastrowid = 10
        self.rowcount = 1

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def execute(self, consulta, parametros=None):
        self.consulta = consulta
        self.parametros = parametros

    def fetchone(self):
        return self.resultado

    def fetchall(self):
        return self.resultados


class ConexaoFake:
    """Simula a conexão com o banco de dados."""

    def __init__(self):
        self.cursor_fake = CursorFake()
        self.commit_chamado = False
        self.rollback_chamado = False

    def cursor(self):
        return self.cursor_fake

    def commit(self):
        self.commit_chamado = True

    def rollback(self):
        self.rollback_chamado = True


def preparar_conexao(monkeypatch):
    """Substitui a conexão real por uma conexão simulada."""

    conexao = ConexaoFake()

    monkeypatch.setattr(
        animal_repository,
        "get_db",
        lambda: conexao
    )

    return conexao


# ==================================================
# TESTES DE CONSULTA
# ==================================================

def test_listar_animais_com_filtros(monkeypatch):
    """Verifica filtros e parâmetros da listagem."""

    conexao = preparar_conexao(monkeypatch)

    animal_repository.listar_animais(
        filtros={
            "identificacao": "BRINCO",
            "especie": "Bovino",
            "situacao": "Ativo"
        },
        limite=20,
        deslocamento=0
    )

    cursor = conexao.cursor_fake

    assert "identificacao LIKE %s" in cursor.consulta
    assert "especie = %s" in cursor.consulta
    assert "situacao = %s" in cursor.consulta

    assert cursor.parametros == [
        "%BRINCO%",
        "Bovino",
        "Ativo",
        20,
        0
    ]


def test_buscar_animal_por_id(monkeypatch):
    """Verifica a busca de animal pelo ID."""

    conexao = preparar_conexao(monkeypatch)

    animal = {
        "id": 5,
        "identificacao": "BRINCO-005"
    }

    conexao.cursor_fake.resultado = animal

    resultado = animal_repository.buscar_animal_por_id(5)

    assert resultado == animal
    assert "WHERE id = %s" in conexao.cursor_fake.consulta
    assert conexao.cursor_fake.parametros == (5,)


def test_buscar_animal_por_identificacao(monkeypatch):
    """Verifica a busca pela identificação."""

    conexao = preparar_conexao(monkeypatch)

    animal = {
        "id": 5,
        "identificacao": "BRINCO-005"
    }

    conexao.cursor_fake.resultado = animal

    resultado = animal_repository.buscar_animal_por_identificacao(
        "BRINCO-005"
    )

    assert resultado == animal
    assert "WHERE identificacao = %s" in conexao.cursor_fake.consulta
    assert conexao.cursor_fake.parametros == ("BRINCO-005",)


# ==================================================
# TESTES DE CADASTRO
# ==================================================

def test_criar_animal_com_sucesso(monkeypatch):
    """Verifica a inserção e confirmação da transação."""

    conexao = preparar_conexao(monkeypatch)

    dados = {
        "identificacao": "BRINCO-010",
        "especie": "Bovino",
        "situacao": "Ativo"
    }

    resultado = animal_repository.criar_animal(
        dados,
        criado_por=1
    )

    assert resultado == 10
    assert "INSERT INTO animais" in conexao.cursor_fake.consulta
    assert conexao.commit_chamado is True
    assert conexao.rollback_chamado is False


# ==================================================
# TESTES DE ATUALIZAÇÃO
# ==================================================

def test_atualizar_animal_com_sucesso(monkeypatch):
    """Verifica a atualização dos dados cadastrais."""

    conexao = preparar_conexao(monkeypatch)

    resultado = animal_repository.atualizar_animal(
        5,
        {"situacao": "Inativo"}
    )

    assert resultado is True
    assert "UPDATE animais" in conexao.cursor_fake.consulta
    assert conexao.cursor_fake.parametros == ["Inativo", 5]
    assert conexao.commit_chamado is True


def test_atualizar_animal_sem_campos(monkeypatch):
    """Verifica a rejeição de atualização sem campos."""

    conexao = preparar_conexao(monkeypatch)

    resultado = animal_repository.atualizar_animal(5, {})

    assert resultado is False
    assert conexao.commit_chamado is False


# ==================================================
# TESTES DE INATIVAÇÃO
# ==================================================

def test_inativar_animal_com_sucesso(monkeypatch):
    """Verifica a inativação sem excluir o registro."""

    conexao = preparar_conexao(monkeypatch)

    resultado = animal_repository.inativar_animal(5)

    assert resultado is True
    assert "SET ativo = 0" in conexao.cursor_fake.consulta
    assert conexao.cursor_fake.parametros == (5,)
    assert conexao.commit_chamado is True
