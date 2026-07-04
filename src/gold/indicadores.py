import pandas as pd

from src.gold.config import EXECUTION_DATE
from src.gold.regras import aplicar_status_meta


# ============================================================
# 1. indicador_meta_brasil
# ============================================================

def construir_indicador_meta_brasil(
    df_resultado_brasil: pd.DataFrame,
    df_meta_brasil: pd.DataFrame,
) -> pd.DataFrame:
    df = df_resultado_brasil.merge(
        df_meta_brasil,
        on=["ano", "rede", "nivel_agregacao"],
        how="left",
    )

    df = df[df["ano"] == df["ano_meta"]].copy()

    df = aplicar_status_meta(df)
    df["data_processamento_gold"] = EXECUTION_DATE

    df = df[
        [
            "ano",
            "rede",
            "nivel_agregacao",
            "taxa_alfabetizacao",
            "percentual_participacao",
            "ano_meta",
            "meta_alfabetizacao",
            "distancia_meta",
            "flag_meta_atingida",
            "status_meta",
            "data_processamento_gold",
        ]
    ].copy()

    return df.sort_values(["ano", "rede"]).reset_index(drop=True)


# ============================================================
# 2. indicador_meta_uf
# ============================================================

def construir_indicador_meta_uf(
    df_resultado_meta_uf: pd.DataFrame,
    df_meta_anual_uf: pd.DataFrame,
    df_dim_uf: pd.DataFrame,
) -> pd.DataFrame:
    df = df_resultado_meta_uf.merge(
        df_meta_anual_uf,
        on=["ano", "sigla_uf", "rede", "nivel_agregacao"],
        how="left",
    )

    df = df[df["ano"] == df["ano_meta"]].copy()

    df = df.merge(df_dim_uf, on="sigla_uf", how="left")

    df = aplicar_status_meta(df)
    df["data_processamento_gold"] = EXECUTION_DATE

    df = df[
        [
            "ano",
            "id_uf",
            "sigla_uf",
            "sigla_uf_nome",
            "nome_regiao",
            "rede",
            "nivel_agregacao",
            "taxa_alfabetizacao",
            "percentual_participacao",
            "ano_meta",
            "meta_alfabetizacao",
            "distancia_meta",
            "flag_meta_atingida",
            "status_meta",
            "data_processamento_gold",
        ]
    ].copy()

    return df.sort_values(["ano", "sigla_uf", "rede"]).reset_index(drop=True)


# ============================================================
# 3. ranking_uf_prioritaria
# ============================================================

def construir_ranking_uf_prioritaria(df_indicador_meta_uf: pd.DataFrame) -> pd.DataFrame:
    df = df_indicador_meta_uf.copy()

    df = df[df["status_meta"] == "Abaixo da meta"].copy()

    df = df.sort_values(
        ["ano", "distancia_meta"], ascending=[True, True]
    ).reset_index(drop=True)

    df["posicao_prioridade"] = df.groupby("ano").cumcount() + 1

    return df[
        [
            "ano",
            "posicao_prioridade",
            "sigla_uf",
            "sigla_uf_nome",
            "nome_regiao",
            "rede",
            "taxa_alfabetizacao",
            "meta_alfabetizacao",
            "distancia_meta",
            "percentual_participacao",
            "status_meta",
            "data_processamento_gold",
        ]
    ].copy()


# ============================================================
# 4. indicador_meta_municipio
# ============================================================

def construir_indicador_meta_municipio(
    df_resultado_meta_municipio: pd.DataFrame,
    df_meta_anual_municipio: pd.DataFrame,
    df_dim_municipio: pd.DataFrame,
) -> pd.DataFrame:
    df = df_resultado_meta_municipio.merge(
        df_meta_anual_municipio,
        on=["ano", "id_municipio", "rede", "nivel_agregacao"],
        how="left",
    )

    df = df[df["ano"] == df["ano_meta"]].copy()

    df = df.merge(df_dim_municipio, on="id_municipio", how="left")

    df = aplicar_status_meta(df)
    df["data_processamento_gold"] = EXECUTION_DATE

    df = df[
        [
            "ano",
            "id_municipio",
            "id_municipio_nome",
            "id_uf",
            "sigla_uf",
            "nome_regiao",
            "rede",
            "nivel_agregacao",
            "taxa_alfabetizacao",
            "percentual_participacao",
            "ano_meta",
            "meta_alfabetizacao",
            "distancia_meta",
            "flag_meta_atingida",
            "status_meta",
            "data_processamento_gold",
        ]
    ].copy()

    return df.sort_values(["ano", "id_municipio", "rede"]).reset_index(drop=True)


# ============================================================
# 5. ranking_municipio_prioritario
# ============================================================

def construir_ranking_municipio_prioritario(
    df_indicador_meta_municipio: pd.DataFrame,
) -> pd.DataFrame:
    df = df_indicador_meta_municipio.copy()

    df = df[df["status_meta"] == "Abaixo da meta"].copy()

    df = df.sort_values(
        ["ano", "distancia_meta"], ascending=[True, True]
    ).reset_index(drop=True)

    df["posicao_prioridade"] = df.groupby("ano").cumcount() + 1

    return df[
        [
            "ano",
            "posicao_prioridade",
            "id_municipio",
            "id_municipio_nome",
            "id_uf",
            "sigla_uf",
            "nome_regiao",
            "rede",
            "taxa_alfabetizacao",
            "meta_alfabetizacao",
            "distancia_meta",
            "percentual_participacao",
            "status_meta",
            "data_processamento_gold",
        ]
    ].copy()


# ============================================================
# 6. evolucao_alfabetizacao
# ============================================================

def _base_evolucao(
    df_indicador_meta_brasil: pd.DataFrame,
    df_indicador_meta_uf: pd.DataFrame,
    df_indicador_meta_municipio: pd.DataFrame,
) -> pd.DataFrame:
    return pd.concat(
        [
            df_indicador_meta_brasil,
            df_indicador_meta_uf,
            df_indicador_meta_municipio,
        ],
        ignore_index=True,
        sort=False,
    )


def construir_evolucao_alfabetizacao(
    df_indicador_meta_brasil: pd.DataFrame,
    df_indicador_meta_uf: pd.DataFrame,
    df_indicador_meta_municipio: pd.DataFrame,
) -> pd.DataFrame:
    df_base = _base_evolucao(
        df_indicador_meta_brasil,
        df_indicador_meta_uf,
        df_indicador_meta_municipio,
    )

    df = df_base.groupby(
        ["ano", "rede", "nivel_agregacao"], as_index=False
    ).agg(
        taxa_alfabetizacao_media=("taxa_alfabetizacao", "mean"),
        meta_alfabetizacao_media=("meta_alfabetizacao", "mean"),
        distancia_media_meta=("distancia_meta", "mean"),
        percentual_participacao_medio=("percentual_participacao", "mean"),
        total_registros=("status_meta", "count"),
        total_meta_atingida=(
            "status_meta",
            lambda x: (x == "Meta atingida").sum(),
        ),
        total_abaixo_meta=(
            "status_meta",
            lambda x: (x == "Abaixo da meta").sum(),
        ),
    )

    df["percentual_meta_atingida"] = (
        df["total_meta_atingida"] / df["total_registros"] * 100
    ).round(2)

    df["data_processamento_gold"] = EXECUTION_DATE

    return df.sort_values(
        ["nivel_agregacao", "ano", "rede"]
    ).reset_index(drop=True)


# ============================================================
# 7. resumo_status_meta
# ============================================================

def construir_resumo_status_meta(
    df_indicador_meta_brasil: pd.DataFrame,
    df_indicador_meta_uf: pd.DataFrame,
    df_indicador_meta_municipio: pd.DataFrame,
) -> pd.DataFrame:
    df_base = _base_evolucao(
        df_indicador_meta_brasil,
        df_indicador_meta_uf,
        df_indicador_meta_municipio,
    )

    df = df_base.groupby(
        ["ano", "rede", "nivel_agregacao", "status_meta"], as_index=False
    ).agg(quantidade=("status_meta", "count"))

    df_total = df.groupby(
        ["ano", "rede", "nivel_agregacao"], as_index=False
    ).agg(total_registros=("quantidade", "sum"))

    df = df.merge(df_total, on=["ano", "rede", "nivel_agregacao"], how="left")

    df["percentual_registros"] = (
        df["quantidade"] / df["total_registros"] * 100
    ).round(2)

    df["data_processamento_gold"] = EXECUTION_DATE

    return df.sort_values(
        ["nivel_agregacao", "ano", "rede", "status_meta"]
    ).reset_index(drop=True)


# ============================================================
# 8. feature_municipio_ano  (tabela analítica para IA)
# ============================================================

def construir_feature_municipio_ano(
    df_indicador_meta_municipio: pd.DataFrame,
    df_dim_municipio: pd.DataFrame,
    df_resultado_municipio: pd.DataFrame,
    df_distribuicao_nivel_municipio: pd.DataFrame,
    df_features_externas: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """
    Tabela de features no grão ano + id_municipio + rede, pronta para
    modelos de predição de alfabetização e análise de desigualdade.

    Consolida:
    - indicador x meta (taxa, meta, distância, status);
    - média de português (fato_resultado_municipio);
    - distribuição de alunos por nível (proporcao_nivel_0..8);
    - chaves territoriais (id_uf, sigla_uf, nome_regiao);
    - alvos: taxa_alfabetizacao (regressão) e meta_atingida (classificação).

    Se `df_features_externas` for informado (join por id_municipio+ano),
    colunas socioeconômicas externas (PIB, IDH, etc.) são anexadas.
    """
    chaves = ["ano", "id_municipio", "rede"]

    base = df_indicador_meta_municipio[
        chaves
        + [
            "id_municipio_nome",
            "taxa_alfabetizacao",
            "meta_alfabetizacao",
            "distancia_meta",
            "flag_meta_atingida",
            "status_meta",
            "percentual_participacao",
        ]
    ].copy()

    # Média de português agregada ao grão município+ano+rede.
    media_port = (
        df_resultado_municipio.groupby(chaves, as_index=False)
        .agg(media_portugues=("media_portugues", "mean"))
    )
    base = base.merge(media_port, on=chaves, how="left")

    # Distribuição por nível: formato longo -> largo (uma coluna por nível).
    dist = df_distribuicao_nivel_municipio.copy()
    dist["nivel_col"] = "proporcao_nivel_" + dist["nivel_alfabetizacao"].astype(
        "Int64"
    ).astype(str)
    dist_wide = (
        dist.pivot_table(
            index=chaves,
            columns="nivel_col",
            values="proporcao_alunos",
            aggfunc="mean",
        )
        .reset_index()
    )
    dist_wide.columns.name = None
    base = base.merge(dist_wide, on=chaves, how="left")

    # Chaves territoriais do diretório.
    colunas_territorio = [
        c
        for c in ["id_municipio", "id_uf", "sigla_uf", "nome_regiao"]
        if c in df_dim_municipio.columns
    ]
    if len(colunas_territorio) > 1:
        base = base.merge(
            df_dim_municipio[colunas_territorio].drop_duplicates("id_municipio"),
            on="id_municipio",
            how="left",
        )

    # Enriquecimento externo opcional (contexto socioeconômico).
    if df_features_externas is not None:
        chaves_ext = [c for c in ["ano", "id_municipio"] if c in df_features_externas.columns]
        base = base.merge(df_features_externas, on=chaves_ext, how="left")

    # Alvos para modelagem.
    base["target_taxa_alfabetizacao"] = base["taxa_alfabetizacao"]
    base["target_meta_atingida"] = (base["flag_meta_atingida"] == True).astype("Int64")

    base["data_processamento_gold"] = EXECUTION_DATE

    ordenar = ["ano", "id_uf", "id_municipio", "rede"]
    ordenar = [c for c in ordenar if c in base.columns]

    return base.sort_values(ordenar).reset_index(drop=True)


# ============================================================
# 9. vulnerabilidade_municipio  (base para clusterização)
# ============================================================

def construir_vulnerabilidade_municipio(
    df_feature_municipio_ano: pd.DataFrame,
) -> pd.DataFrame:
    """
    Recorte de municípios abaixo da meta, com um índice de vulnerabilidade
    educacional pronto para clusterização (ex.: K-Means).

    O índice combina dois sinais disponíveis, normalizados por ano:
    - distância da meta (quanto mais negativa, mais vulnerável);
    - proporção de alunos nos níveis mais baixos (0, 1 e 2).

    Municípios com meta atingida ou sem informação ficam fora do recorte.
    """
    df = df_feature_municipio_ano.copy()
    df = df[df["status_meta"] == "Abaixo da meta"].copy()

    if df.empty:
        return df

    # Proporção de alunos em níveis baixos (0 a 2), quando disponível.
    colunas_baixo = [
        c for c in ["proporcao_nivel_0", "proporcao_nivel_1", "proporcao_nivel_2"]
        if c in df.columns
    ]
    if colunas_baixo:
        df["proporcao_niveis_baixos"] = df[colunas_baixo].sum(axis=1, min_count=1)
    else:
        df["proporcao_niveis_baixos"] = pd.NA

    def _normalizar(serie: pd.Series) -> pd.Series:
        minimo, maximo = serie.min(), serie.max()
        if pd.isna(minimo) or pd.isna(maximo) or maximo == minimo:
            return pd.Series(0.0, index=serie.index)
        return (serie - minimo) / (maximo - minimo)

    partes = []
    for _, grupo in df.groupby("ano"):
        g = grupo.copy()
        # gap positivo = distância abaixo da meta (quanto falta)
        gap = (-g["distancia_meta"]).clip(lower=0)
        score_gap = _normalizar(gap)
        score_niveis = _normalizar(g["proporcao_niveis_baixos"].astype(float))
        g["indice_vulnerabilidade"] = (0.6 * score_gap + 0.4 * score_niveis).round(4)
        g = g.sort_values("indice_vulnerabilidade", ascending=False)
        g["posicao_vulnerabilidade"] = range(1, len(g) + 1)
        limite = g["indice_vulnerabilidade"].quantile(0.75)
        g["flag_prioridade_alta"] = g["indice_vulnerabilidade"] >= limite
        partes.append(g)

    df = pd.concat(partes, ignore_index=True)

    colunas = [
        "ano",
        "posicao_vulnerabilidade",
        "id_municipio",
        "id_municipio_nome",
        "id_uf",
        "sigla_uf",
        "nome_regiao",
        "rede",
        "taxa_alfabetizacao",
        "meta_alfabetizacao",
        "distancia_meta",
        "media_portugues",
        "proporcao_niveis_baixos",
        "indice_vulnerabilidade",
        "flag_prioridade_alta",
        "data_processamento_gold",
    ]
    colunas = [c for c in colunas if c in df.columns]

    return df[colunas].sort_values(["ano", "posicao_vulnerabilidade"]).reset_index(drop=True)


# ============================================================
# 10. indicador_meta_regiao  (indicador vs meta agregado por região)
# ============================================================

def construir_indicador_meta_regiao(
    df_indicador_meta_uf: pd.DataFrame,
) -> pd.DataFrame:
    """
    Agrega o indicador vs. meta ao nível das 5 regiões geográficas,
    a partir de indicador_meta_uf (que já carrega nome_regiao).

    As médias são simples entre as UFs da região (não ponderadas por
    população) — leitura executiva; para análise fina, use o grão de UF
    ou de município.
    """
    df = df_indicador_meta_uf.dropna(subset=["nome_regiao"]).copy()

    agg = (
        df.groupby(["ano", "rede", "nome_regiao"], as_index=False)
        .agg(
            taxa_alfabetizacao_media=("taxa_alfabetizacao", "mean"),
            meta_alfabetizacao_media=("meta_alfabetizacao", "mean"),
            distancia_media_meta=("distancia_meta", "mean"),
            total_uf=("sigla_uf", "nunique"),
            total_uf_meta_atingida=(
                "status_meta",
                lambda x: (x == "Meta atingida").sum(),
            ),
        )
    )

    agg["percentual_uf_meta_atingida"] = (
        agg["total_uf_meta_atingida"] / agg["total_uf"] * 100
    ).round(2)

    atingida = agg["taxa_alfabetizacao_media"] >= agg["meta_alfabetizacao_media"]
    sem_info = (
        agg["taxa_alfabetizacao_media"].isna() | agg["meta_alfabetizacao_media"].isna()
    )
    agg["status_meta_regiao"] = "Sem informação"
    agg.loc[atingida & ~sem_info, "status_meta_regiao"] = "Meta atingida"
    agg.loc[~atingida & ~sem_info, "status_meta_regiao"] = "Abaixo da meta"

    for coluna in [
        "taxa_alfabetizacao_media",
        "meta_alfabetizacao_media",
        "distancia_media_meta",
    ]:
        agg[coluna] = agg[coluna].round(2)

    agg["data_processamento_gold"] = EXECUTION_DATE

    return agg.sort_values(["ano", "rede", "nome_regiao"]).reset_index(drop=True)


# ============================================================
# 11. contagem_alunos_territorio  (volume de alunos por território)
# ============================================================

def construir_contagem_alunos_territorio(
    df_fato_aluno: pd.DataFrame,
    df_dim_municipio: pd.DataFrame,
) -> pd.DataFrame:
    """
    Quantidade de alunos por ano, região, UF, município e rede.

    Duas métricas de volume:
    - alunos_avaliados: contagem de alunos distintos na base (amostra);
    - alunos_estimados: soma do peso amostral (peso_aluno), que expande
      a amostra para a população estimada de crianças representadas.

    Agrupando por diferentes colunas obtém-se o volume em qualquer nível:
    nome_regiao (região), sigla_uf (estado) ou id_municipio (cidade).
    """
    df = df_fato_aluno.copy()

    chaves = ["ano", "nome_regiao", "id_uf", "sigla_uf", "id_municipio", "rede"]

    agg = (
        df.groupby(chaves, as_index=False)
        .agg(
            alunos_avaliados=("id_aluno", "nunique"),
            alunos_estimados=("peso_aluno", "sum"),
        )
    )
    agg["alunos_estimados"] = agg["alunos_estimados"].round(0)

    # Nome do município a partir da dimensão.
    agg = agg.merge(
        df_dim_municipio[["id_municipio", "id_municipio_nome"]].drop_duplicates(
            "id_municipio"
        ),
        on="id_municipio",
        how="left",
    )

    agg["data_processamento_gold"] = EXECUTION_DATE

    colunas = [
        "ano",
        "nome_regiao",
        "id_uf",
        "sigla_uf",
        "id_municipio",
        "id_municipio_nome",
        "rede",
        "alunos_avaliados",
        "alunos_estimados",
        "data_processamento_gold",
    ]

    return agg[colunas].sort_values(
        ["ano", "nome_regiao", "sigla_uf", "id_municipio", "rede"]
    ).reset_index(drop=True)


# ============================================================
# 12. taxa_alfabetizacao_por_aluno  (taxa calculada do grão de aluno)
# ============================================================

PONTO_CORTE_ALFABETIZACAO = 743  # ponto de corte do Saeb (Alfabetiza Brasil)


def construir_taxa_alfabetizacao_por_aluno(
    df_fato_aluno: pd.DataFrame,
    df_dim_municipio: pd.DataFrame,
) -> pd.DataFrame:
    """
    Taxa de alfabetização calculada a partir do grão de aluno, aplicando
    o ponto de corte de 743 na proficiência (>= 743 => alfabetizado).

    Métricas por ano, região, UF, município e rede:
    - alunos_com_proficiencia: alunos com proficiência informada;
    - alunos_alfabetizados: alunos com proficiência >= 743;
    - taxa_alfabetizacao_calculada: % simples de alfabetizados;
    - taxa_alfabetizacao_ponderada: % ponderado pelo peso amostral.

    Serve para validar a taxa oficial da base e para análises próprias.
    """
    df = df_fato_aluno.copy()
    df = df[df["proficiencia"].notna()].copy()

    df["alfabetizado_calc"] = (df["proficiencia"] >= PONTO_CORTE_ALFABETIZACAO).astype(int)
    df["peso_aluno"] = pd.to_numeric(df["peso_aluno"], errors="coerce").fillna(0)
    df["peso_alfabetizado"] = df["peso_aluno"] * df["alfabetizado_calc"]

    chaves = ["ano", "nome_regiao", "id_uf", "sigla_uf", "id_municipio", "rede"]

    agg = (
        df.groupby(chaves, as_index=False)
        .agg(
            alunos_com_proficiencia=("id_aluno", "nunique"),
            alunos_alfabetizados=("alfabetizado_calc", "sum"),
            peso_total=("peso_aluno", "sum"),
            peso_alfabetizado=("peso_alfabetizado", "sum"),
        )
    )

    agg["taxa_alfabetizacao_calculada"] = (
        agg["alunos_alfabetizados"] / agg["alunos_com_proficiencia"] * 100
    ).round(2)

    agg["taxa_alfabetizacao_ponderada"] = (
        (agg["peso_alfabetizado"] / agg["peso_total"] * 100)
        .where(agg["peso_total"] > 0)
        .round(2)
    )

    agg = agg.merge(
        df_dim_municipio[["id_municipio", "id_municipio_nome"]].drop_duplicates(
            "id_municipio"
        ),
        on="id_municipio",
        how="left",
    )

    agg["data_processamento_gold"] = EXECUTION_DATE

    colunas = [
        "ano",
        "nome_regiao",
        "id_uf",
        "sigla_uf",
        "id_municipio",
        "id_municipio_nome",
        "rede",
        "alunos_com_proficiencia",
        "alunos_alfabetizados",
        "taxa_alfabetizacao_calculada",
        "taxa_alfabetizacao_ponderada",
        "data_processamento_gold",
    ]

    return agg[colunas].sort_values(
        ["ano", "nome_regiao", "sigla_uf", "id_municipio", "rede"]
    ).reset_index(drop=True)
