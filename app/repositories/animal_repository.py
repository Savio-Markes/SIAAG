# Desenvolvido por: Fábio Barbosa

from app.extensions import get_db


def _montar_condicoes(filtros=None):
    filtros = filtros or {}
    condicoes = ["1 = 1"]
    parametros = []

    if filtros.get("identificacao"):
        condicoes.append("identificacao LIKE %s")
        parametros.append(f"%{filtros['identificacao']}%")

    if filtros.get("especie"):
        condicoes.append("especie = %s")
        parametros.append(filtros["especie"])

    if filtros.get("situacao"):
        condicoes.append("situacao = %s")
        parametros.append(filtros["situacao"])

    if filtros.get("ativo") in (0, 1, "0", "1"):
        condicoes.append("ativo = %s")
        parametros.append(int(filtros["ativo"]))

    return " AND ".join(condicoes), parametros


def listar_animais(filtros=None, limite=50, deslocamento=0):
    condicoes, parametros = _montar_condicoes(filtros)

    consulta = f"""
        SELECT
            id, identificacao, nome, especie, raca, sexo,
            nascimento, origem, data_entrada, localizacao,
            situacao, observacoes, ativo, criado_por,
            criado_em, atualizado_em
        FROM animais
        WHERE {condicoes}
        ORDER BY id DESC
        LIMIT %s OFFSET %s
    """

    parametros.extend([limite, deslocamento])
    conexao = get_db()

    with conexao.cursor() as cursor:
        cursor.execute(consulta, parametros)
        return cursor.fetchall()


def contar_animais(filtros=None):
    condicoes, parametros = _montar_condicoes(filtros)

    consulta = f"""
        SELECT COUNT(*) AS total
        FROM animais
        WHERE {condicoes}
    """

    conexao = get_db()

    with conexao.cursor() as cursor:
        cursor.execute(consulta, parametros)
        resultado = cursor.fetchone()
        return resultado["total"]


def buscar_animal_por_id(animal_id):
    consulta = "SELECT * FROM animais WHERE id = %s"
    conexao = get_db()

    with conexao.cursor() as cursor:
        cursor.execute(consulta, (animal_id,))
        return cursor.fetchone()


def buscar_animal_por_identificacao(identificacao):
    consulta = """
        SELECT *
        FROM animais
        WHERE identificacao = %s
        LIMIT 1
    """

    conexao = get_db()

    with conexao.cursor() as cursor:
        cursor.execute(consulta, (identificacao,))
        return cursor.fetchone()


def criar_animal(dados, criado_por):
    consulta = """
        INSERT INTO animais (
            identificacao, nome, especie, raca, sexo,
            nascimento, origem, data_entrada, localizacao,
            situacao, observacoes, criado_por,
            criado_em, atualizado_em
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, NOW(), NOW()
        )
    """

    parametros = (
        dados["identificacao"],
        dados.get("nome"),
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
    campos_permitidos = (
        "identificacao", "nome", "especie", "raca", "sexo",
        "nascimento", "origem", "data_entrada", "localizacao",
        "situacao", "observacoes"
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
    consulta = """
        UPDATE animais
        SET ativo = 0,
            atualizado_em = NOW()
        WHERE id = %s AND ativo = 1
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


def reativar_animal(animal_id):
    consulta = """
        UPDATE animais
        SET ativo = 1,
            atualizado_em = NOW()
        WHERE id = %s AND ativo = 0
    """

    conexao = get_db()

    try:
        with conexao.cursor() as cursor:
            cursor.execute(consulta, (animal_id,))
            reativado = cursor.rowcount > 0

        conexao.commit()
        return reativado

    except Exception:
        conexao.rollback()
        raise


def contar_animais_ativos():
    consulta = """
        SELECT COUNT(*) AS total
        FROM animais
        WHERE ativo = 1
    """

    conexao = get_db()

    with conexao.cursor() as cursor:
        cursor.execute(consulta)
        return cursor.fetchone()["total"]


def contar_animais_por_especie():
    consulta = """
        SELECT especie, COUNT(*) AS total
        FROM animais
        WHERE ativo = 1
        GROUP BY especie
        ORDER BY especie
    """

    conexao = get_db()

    with conexao.cursor() as cursor:
        cursor.execute(consulta)
        return cursor.fetchall()


def contar_animais_por_situacao():
    consulta = """
        SELECT situacao, COUNT(*) AS total
        FROM animais
        WHERE ativo = 1
        GROUP BY situacao
        ORDER BY situacao
    """

    conexao = get_db()

    with conexao.cursor() as cursor:
        cursor.execute(consulta)
        return cursor.fetchall()