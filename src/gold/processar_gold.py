import pandas as pd

from src.gold.gravadores import salvar_gold
from src.gold.leitores import carregar_silver
from src.gold import indicadores as ind


CODIGO_UF_POR_SIGLA = {
    "RO": "11",
    "AC": "12",
    "AM": "13",
    "RR": "14",
    "PA": "15",
    "AP": "16",
    "TO": "17",
    "MA": "21",
    "PI": "22",
    "CE": "23",
    "RN": "24",
    "PB": "25",
    "PE": "26",
    "AL": "27",
    "SE": "28",
    "BA": "29",
    "MG": "31",
    "ES": "32",
    "RJ": "33",
    "SP": "35",
    "PR": "41",
    "SC": "42",
    "RS": "43",
    "MS": "50",
    "MT": "51",
    "GO": "52",
    "DF": "53",
}

SIGLA_UF_POR_CODIGO = {codigo: sigla for sigla, codigo in CODIGO_UF_POR_SIGLA.items()}
REGIAO_POR_SIGLA_UF = {
    "RO": "Norte",
    "AC": "Norte",
    "AM": "Norte",
    "RR": "Norte",
    "PA": "Norte",
    "AP": "Norte",
    "TO": "Norte",
    "MA": "Nordeste",
    "PI": "Nordeste",
    "CE": "Nordeste",
    "RN": "Nordeste",
    "PB": "Nordeste",
    "PE": "Nordeste",
    "AL": "Nordeste",
    "SE": "Nordeste",
    "BA": "Nordeste",
    "MG": "Sudeste",
    "ES": "Sudeste",
    "RJ": "Sudeste",
    "SP": "Sudeste",
    "PR": "Sul",
    "SC": "Sul",
    "RS": "Sul",
    "MS": "Centro-Oeste",
    "MT": "Centro-Oeste",
    "GO": "Centro-Oeste",
    "DF": "Centro-Oeste",
}


def enriquecer_dim_uf(df_dim_uf: pd.DataFrame) -> pd.DataFrame:
    df = df_dim_uf.copy()

    if "nome_regiao" not in df.columns and "regiao_brasil" in df.columns:
        df = df.rename(columns={"regiao_brasil": "nome_regiao"})

    df["id_uf"] = df["sigla_uf"].map(CODIGO_UF_POR_SIGLA)

    if "nome_regiao" not in df.columns:
        df["nome_regiao"] = df["sigla_uf"].map(REGIAO_POR_SIGLA_UF)

    return df


def enriquecer_dim_municipio(df_dim_municipio: pd.DataFrame) -> pd.DataFrame:
    df = df_dim_municipio.copy()
    df["id_uf"] = df["id_municipio"].astype(str).str[:2]
    df["sigla_uf"] = df["id_uf"].map(SIGLA_UF_POR_CODIGO)
    df["nome_regiao"] = df["sigla_uf"].map(REGIAO_POR_SIGLA_UF)

    return df


def enriquecer_fato_com_territorio(
    df_fato: pd.DataFrame,
    df_dim_municipio: pd.DataFrame,
) -> pd.DataFrame:
    colunas_territorio = ["id_municipio", "id_uf", "sigla_uf", "nome_regiao"]
    df_territorio = df_dim_municipio[colunas_territorio].drop_duplicates("id_municipio")

    return df_fato.merge(df_territorio, on="id_municipio", how="left")


def processar_camada_gold() -> dict[str, pd.DataFrame]:
    """
    Processa toda a camada Gold consumindo exclusivamente a Silver.

    Diferença em relação à versão anterior (notebook 04): não há mais
    a etapa garantir_silver_meta_municipio lendo da Bronze. As metas
    municipais agora são produzidas na própria Silver
    (fato_resultado_meta_municipio e fato_meta_anual_municipio).
    """
    print("Iniciando processamento da camada gold")

    tabelas: dict[str, pd.DataFrame] = {}

    # ------------------------------------------------------------
    # 1. indicador_meta_brasil
    # ------------------------------------------------------------
    print("\n1. Gerando gold.indicador_meta_brasil")

    df_resultado_brasil = carregar_silver(
        "fato_resultado_brasil",
        ["ano", "rede", "taxa_alfabetizacao", "percentual_participacao", "nivel_agregacao"],
    )
    df_meta_brasil = carregar_silver(
        "fato_meta_anual_brasil",
        ["ano", "rede", "ano_meta", "meta_alfabetizacao", "nivel_agregacao"],
    )

    tabelas["indicador_meta_brasil"] = ind.construir_indicador_meta_brasil(
        df_resultado_brasil, df_meta_brasil
    )

    # ------------------------------------------------------------
    # 2. indicador_meta_uf
    # ------------------------------------------------------------
    print("\n2. Gerando gold.indicador_meta_uf")

    df_resultado_meta_uf = carregar_silver(
        "fato_resultado_meta_uf",
        [
            "ano", "sigla_uf", "rede",
            "taxa_alfabetizacao", "percentual_participacao", "nivel_agregacao",
        ],
    )
    df_meta_anual_uf = carregar_silver(
        "fato_meta_anual_uf",
        ["ano", "sigla_uf", "rede", "ano_meta", "meta_alfabetizacao", "nivel_agregacao"],
    )
    df_dim_uf = enriquecer_dim_uf(
        carregar_silver("dim_uf", ["sigla_uf", "sigla_uf_nome", "regiao_brasil"])
    )

    tabelas["indicador_meta_uf"] = ind.construir_indicador_meta_uf(
        df_resultado_meta_uf, df_meta_anual_uf, df_dim_uf
    )

    # ------------------------------------------------------------
    # 3. ranking_uf_prioritaria
    # ------------------------------------------------------------
    print("\n3. Gerando gold.ranking_uf_prioritaria")

    tabelas["ranking_uf_prioritaria"] = ind.construir_ranking_uf_prioritaria(
        tabelas["indicador_meta_uf"]
    )

    # ------------------------------------------------------------
    # 4. indicador_meta_municipio
    # ------------------------------------------------------------
    print("\n4. Gerando gold.indicador_meta_municipio")

    df_resultado_meta_municipio = carregar_silver(
        "fato_resultado_meta_municipio",
        [
            "ano", "id_municipio", "rede",
            "taxa_alfabetizacao", "percentual_participacao", "nivel_agregacao",
        ],
    )
    df_meta_anual_municipio = carregar_silver(
        "fato_meta_anual_municipio",
        ["ano", "id_municipio", "rede", "ano_meta", "meta_alfabetizacao", "nivel_agregacao"],
    )
    df_dim_municipio = enriquecer_dim_municipio(
        carregar_silver("dim_municipio", ["id_municipio", "id_municipio_nome"])
    )

    tabelas["indicador_meta_municipio"] = ind.construir_indicador_meta_municipio(
        df_resultado_meta_municipio, df_meta_anual_municipio, df_dim_municipio
    )

    # ------------------------------------------------------------
    # 5. ranking_municipio_prioritario
    # ------------------------------------------------------------
    print("\n5. Gerando gold.ranking_municipio_prioritario")

    tabelas["ranking_municipio_prioritario"] = ind.construir_ranking_municipio_prioritario(
        tabelas["indicador_meta_municipio"]
    )

    # ------------------------------------------------------------
    # 6. evolucao_alfabetizacao
    # ------------------------------------------------------------
    print("\n6. Gerando gold.evolucao_alfabetizacao")

    tabelas["evolucao_alfabetizacao"] = ind.construir_evolucao_alfabetizacao(
        tabelas["indicador_meta_brasil"],
        tabelas["indicador_meta_uf"],
        tabelas["indicador_meta_municipio"],
    )

    # ------------------------------------------------------------
    # 7. resumo_status_meta
    # ------------------------------------------------------------
    print("\n7. Gerando gold.resumo_status_meta")

    tabelas["resumo_status_meta"] = ind.construir_resumo_status_meta(
        tabelas["indicador_meta_brasil"],
        tabelas["indicador_meta_uf"],
        tabelas["indicador_meta_municipio"],
    )

    # ------------------------------------------------------------
    # 8. feature_municipio_ano (tabela para IA)
    # ------------------------------------------------------------
    print("\n8. Gerando gold.feature_municipio_ano")

    df_dim_municipio_enr = enriquecer_dim_municipio(carregar_silver("dim_municipio"))
    df_resultado_municipio = carregar_silver(
        "fato_resultado_municipio",
        ["ano", "id_municipio", "rede", "media_portugues"],
    )
    df_distribuicao_municipio = carregar_silver(
        "fato_distribuicao_nivel_municipio",
        ["ano", "id_municipio", "rede", "nivel_alfabetizacao", "proporcao_alunos"],
    )

    tabelas["feature_municipio_ano"] = ind.construir_feature_municipio_ano(
        tabelas["indicador_meta_municipio"],
        df_dim_municipio_enr,
        df_resultado_municipio,
        df_distribuicao_municipio,
    )

    # ------------------------------------------------------------
    # 9. vulnerabilidade_municipio (base para clusterização)
    # ------------------------------------------------------------
    print("\n9. Gerando gold.vulnerabilidade_municipio")

    tabelas["vulnerabilidade_municipio"] = ind.construir_vulnerabilidade_municipio(
        tabelas["feature_municipio_ano"]
    )

    # ------------------------------------------------------------
    # 10. indicador_meta_regiao
    # ------------------------------------------------------------
    print("\n10. Gerando gold.indicador_meta_regiao")

    tabelas["indicador_meta_regiao"] = ind.construir_indicador_meta_regiao(
        tabelas["indicador_meta_uf"]
    )

    # ------------------------------------------------------------
    # 11. contagem_alunos_territorio
    # ------------------------------------------------------------
    print("\n11. Gerando gold.contagem_alunos_territorio")

    df_fato_aluno = enriquecer_fato_com_territorio(
        carregar_silver(
            "fato_aluno_alfabetizacao",
            ["ano", "id_aluno", "id_municipio", "rede", "proficiencia", "peso_aluno"],
        ),
        df_dim_municipio,
    )

    tabelas["contagem_alunos_territorio"] = ind.construir_contagem_alunos_territorio(
        df_fato_aluno, df_dim_municipio
    )

    # ------------------------------------------------------------
    # 12. taxa_alfabetizacao_por_aluno
    # ------------------------------------------------------------
    print("\n12. Gerando gold.taxa_alfabetizacao_por_aluno")

    tabelas["taxa_alfabetizacao_por_aluno"] = ind.construir_taxa_alfabetizacao_por_aluno(
        df_fato_aluno, df_dim_municipio
    )

    # ------------------------------------------------------------
    # Salvamento
    # ------------------------------------------------------------
    print("\nSalvando tabelas gold")

    for nome_tabela, df in tabelas.items():
        salvar_gold(df, nome_tabela)

    print("\nProcessamento da camada gold finalizado")

    return tabelas
