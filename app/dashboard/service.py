
# Desenvolvido por: Fábio Barbosa

from app.repositories.animal_repository import (
    contar_animais,
    contar_animais_ativos,
    contar_animais_por_especie,
    contar_animais_por_situacao,
)


def obter_dados_dashboard():
    """Obtém indicadores reais para o painel principal."""

    total_animais = contar_animais()
    animais_ativos = contar_animais_ativos()

    especies = contar_animais_por_especie()
    situacoes = contar_animais_por_situacao()

    return {
        "total_animais": total_animais,
        "animais_ativos": animais_ativos,
        "animais_inativos": total_animais - animais_ativos,
        "especies": especies,
        "situacoes": situacoes,
    }
