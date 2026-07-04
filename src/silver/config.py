from pathlib import Path


BRONZE_PATH = Path("data/bronze")
SILVER_PATH = Path("data/silver")


ENTIDADES_BRONZE_SILVER = [
    "uf",
    "municipio",
    "meta_alfabetizacao_brasil",
    "meta_alfabetizacao_uf",
    "meta_alfabetizacao_municipio",
    "alunos",
]


COLUNAS_NIVEIS = [
    "proporcao_aluno_nivel_0",
    "proporcao_aluno_nivel_1",
    "proporcao_aluno_nivel_2",
    "proporcao_aluno_nivel_3",
    "proporcao_aluno_nivel_4",
    "proporcao_aluno_nivel_5",
    "proporcao_aluno_nivel_6",
    "proporcao_aluno_nivel_7",
    "proporcao_aluno_nivel_8",
]


COLUNAS_METAS = [
    "meta_alfabetizacao_2024",
    "meta_alfabetizacao_2025",
    "meta_alfabetizacao_2026",
    "meta_alfabetizacao_2027",
    "meta_alfabetizacao_2028",
    "meta_alfabetizacao_2029",
    "meta_alfabetizacao_2030",
]


COLUNAS_NUMERICAS_RESULTADO = [
    "taxa_alfabetizacao",
    "media_portugues",
    *COLUNAS_NIVEIS,
]


COLUNAS_NUMERICAS_META = [
    "taxa_alfabetizacao",
    *COLUNAS_METAS,
    "percentual_participacao",
]


MAPA_REGIAO_UF = {
    "AC": "Norte",
    "AL": "Nordeste",
    "AP": "Norte",
    "AM": "Norte",
    "BA": "Nordeste",
    "CE": "Nordeste",
    "DF": "Centro-Oeste",
    "ES": "Sudeste",
    "GO": "Centro-Oeste",
    "MA": "Nordeste",
    "MT": "Centro-Oeste",
    "MS": "Centro-Oeste",
    "MG": "Sudeste",
    "PA": "Norte",
    "PB": "Nordeste",
    "PR": "Sul",
    "PE": "Nordeste",
    "PI": "Nordeste",
    "RJ": "Sudeste",
    "RN": "Nordeste",
    "RS": "Sul",
    "RO": "Norte",
    "RR": "Norte",
    "SC": "Sul",
    "SP": "Sudeste",
    "SE": "Nordeste",
    "TO": "Norte",
}
