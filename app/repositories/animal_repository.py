
from app.extensions import get_db


def listar_animais(filtros=None, limite=50, deslocamento=0):
    """Lista animais com filtros opcionais e paginação."""

    filtros = filtros or {}

    consulta = """
        SELECT
            id,
            nome,
            especie,
            raca,
            sexo,
            nascimento,
            origem,
            data_entrada,
            localizacao,
            situacao,
            observacoes,
            ativo,
            criado_por,
            criado_em,
            atualizado_em
        FROM animais
        WHERE 1 = 1
    """

    parametros = []

    if filtros.get("nome"):
        consulta += " AND nome LIKE %s"
        parametros.append(f"%{filtros['nome']}%")

    if filtros.get("especie"):
        consulta += " AND especie = %s"
        parametros.append(filtros["especie"])

    if filtros.get("situacao"):
        consulta += " AND situacao = %s"
        parametros.append(filtros["situacao"])

    consulta += """
        ORDER BY id DESC
        LIMIT %s OFFSET %s
    """

    parametros.extend([limite, deslocamento])

    conexao = get_db()

    with conexao.cursor() as cursor:
        cursor.execute(consulta, parametros)
        return cursor.fetchall()


def buscar_animal_por_id(animal_id):
    """Busca um animal pelo ID."""

    consulta = """
        SELECT *
        FROM animais
        WHERE id = %s
    """

    conexao = get_db()

    with conexao.cursor() as cursor:
        cursor.execute(consulta, (animal_id,))
        return cursor.fetchone()


def criar_animal(dados, criado_por):
    """Insere um novo animal no banco de dados."""

    consulta = """
        INSERT INTO animais (
            nome,
            especie,
            raca,
            sexo,
            nascimento,
            origem,
            data_entrada,
            localizacao,
            situacao,
            observacoes,
            criado_por,
            criado_em,
            atualizado_em
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, NOW(), NOW()
        )
    """

    parametros = (
        dados["nome"],
        dados["especie"],
        dados.get("raca"),
        dados.get("sexo"),
        dados.get("nascimento"),
        dados.get("origem"),
        dados.get("data_entrada"),
        dados.get("localizacao"),
        dados["situacao"],
        dados.get("observacoes"),
        criado_por
    )

    conexao = get_db()

    try:
        with conexao.cursor() as cursor:
            cursor.execute(consulta, parametros)
            animal_id = cursor.lastrowid

        conexao.commit()
        return animal_id

    except Exception:
        conexao.rollback()
        raise


def atualizar_animal(animal_id, dados):
    """Atualiza os dados cadastrais do animal."""

    campos_permitidos = (
        "nome",
        "especie",
        "raca",
        "sexo",
        "nascimento",
        "origem",
        "data_entrada",
        "localizacao",
        "situacao",
        "observacoes",
        "ativo"
    )

    campos = []
    parametros = []

    for campo in campos_permitidos:
        if campo in dados:
            campos.append(f"{campo} = %s")
            parametros.append(dados[campo])

    if not campos:
        return False

    campos.append("atualizado_em = NOW()")

    consulta = f"""
        UPDATE animais
        SET {", ".join(campos)}
        WHERE id = %s
    """

    parametros.append(animal_id)

    conexao = get_db()

    try:
        with conexao.cursor() as cursor:
            cursor.execute(consulta, parametros)
            atualizado = cursor.rowcount > 0

        conexao.commit()
        return atualizado

    except Exception:
        conexao.rollback()
        raise


def inativar_animal(animal_id):
    """Inativa um animal sem excluir seu histórico."""

    consulta = """
        UPDATE animais
        SET ativo = 0,
            atualizado_em = NOW()
        WHERE id = %s
    """

    conexao = get_db()

    try:
        with conexao.cursor() as cursor:
            cursor.execute(consulta, (animal_id,))
            inativado = cursor.rowcount > 0

        conexao.commit()
        return inativado

    except Exception:
        conexao.rollback()
        raise
