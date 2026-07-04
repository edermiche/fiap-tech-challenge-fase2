"""
Processador da camada Gold - Análises finais de alfabetização.
"""
from datetime import date
from pathlib import Path

import pandas as pd


SILVER_PATH = Path("data/silver")
GOLD_PATH = Path("data/gold")

EXECUTION_DATE = date.today().isoformat()


def localizar_parquet_mais_recente(caminho_tabela: Path) -> Path:
    """Localiza o arquivo Parquet mais recente em uma pasta."""
    arquivos = list(caminho_tabela.rglob("*.parquet"))
    
    if not arquivos:
        raise FileNotFoundError(f"Nenhum arquivo Parquet encontrado em: {caminho_tabela}")
    
    return max(arquivos, key=lambda arquivo: arquivo.stat().st_mtime)


def carregar_silver(nome_tabela: str, colunas: list[str] | None = None) -> pd.DataFrame:
    """Carrega uma tabela Silver pelo nome."""
    caminho_tabela = SILVER_PATH / nome_tabela
    arquivo = localizar_parquet_mais_recente(caminho_tabela)
    
    df = pd.read_parquet(arquivo, columns=colunas)
    
    print(f"[OK] silver.{nome_tabela} carregada: {len(df)} linhas")
    
    return df


def salvar_gold(df: pd.DataFrame, nome_tabela: str) -> Path:
    """Salva uma tabela Gold com particionamento por data."""
    output_dir = GOLD_PATH / nome_tabela / f"execution_date={EXECUTION_DATE}"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / f"{nome_tabela}.parquet"
    df.to_parquet(output_file, index=False)
    
    print(f"[OK] gold.{nome_tabela} salva: {len(df)} linhas")
    
    return output_file


def aplicar_status_meta(df: pd.DataFrame) -> pd.DataFrame:
    """Calcula status de cumprimento de meta."""
    df = df.copy()
    
    df["distancia_meta"] = df["taxa_alfabetizacao"] - df["meta_alfabetizacao"]
    df["flag_meta_atingida"] = pd.NA
    df.loc[
        ~(df["taxa_alfabetizacao"].isna() | df["meta_alfabetizacao"].isna()),
        "flag_meta_atingida"
    ] = df.loc[
        ~(df["taxa_alfabetizacao"].isna() | df["meta_alfabetizacao"].isna()),
        "distancia_meta"
    ] >= 0
    
    df["status_meta"] = "Sem informação"
    df.loc[df["flag_meta_atingida"] == True, "status_meta"] = "Meta atingida"
    df.loc[df["flag_meta_atingida"] == False, "status_meta"] = "Abaixo da meta"
    
    return df


def processar_indicador_meta_brasil(
    df_fato_resultado_brasil: pd.DataFrame,
    df_fato_meta_anual_brasil: pd.DataFrame,
) -> pd.DataFrame:
    """Processa indicador de meta Brasil."""
    df = (
        df_fato_resultado_brasil
        .merge(
            df_fato_meta_anual_brasil,
            on=["ano", "rede", "nivel_agregacao"],
            how="inner",
            suffixes=("_resultado", "_meta")
        )
    )

    # Compara o resultado observado no ano apenas com a meta do mesmo ano;
    # sem esse filtro, cada linha de resultado se multiplica por uma linha
    # por ano_meta (2024..2030), comparando o mesmo resultado contra metas
    # de anos diferentes.
    df = df[df["ano"] == df["ano_meta"]].copy()

    df = aplicar_status_meta(df)

    return (
        df
        .sort_values(["ano", "rede"])
        .reset_index(drop=True)
    )


def processar_indicador_meta_uf(
    df_fato_resultado_meta_uf: pd.DataFrame,
    df_fato_meta_anual_uf: pd.DataFrame,
) -> pd.DataFrame:
    """Processa indicador de meta por UF."""
    df = (
        df_fato_resultado_meta_uf
        .merge(
            df_fato_meta_anual_uf,
            on=["ano", "sigla_uf", "rede", "nivel_agregacao"],
            how="inner",
            suffixes=("_resultado", "_meta")
        )
    )

    df = df[df["ano"] == df["ano_meta"]].copy()

    df = aplicar_status_meta(df)

    return (
        df
        .sort_values(["ano", "sigla_uf", "rede"])
        .reset_index(drop=True)
    )


def processar_ranking_uf_prioritaria(
    df_indicador_meta_uf: pd.DataFrame,
) -> pd.DataFrame:
    """Processa ranking de UFs prioritárias."""
    df = (
        df_indicador_meta_uf[df_indicador_meta_uf["status_meta"] == "Abaixo da meta"]
        .groupby(["ano", "sigla_uf"])
        .agg({
            "distancia_meta": "mean",
            "taxa_alfabetizacao": "mean",
        })
        .reset_index()
        .sort_values(["ano", "distancia_meta"])
        .reset_index(drop=True)
    )
    
    df["ranking"] = df.groupby("ano").cumcount() + 1
    
    return df[df["ranking"] <= 10].reset_index(drop=True)


def processar_indicador_meta_municipio(
    df_fato_resultado_meta_municipio: pd.DataFrame,
    df_fato_meta_anual_municipio: pd.DataFrame,
) -> pd.DataFrame:
    """Processa indicador de meta por município."""
    df = (
        df_fato_resultado_meta_municipio
        .merge(
            df_fato_meta_anual_municipio,
            on=["ano", "id_municipio", "rede", "nivel_agregacao"],
            how="inner",
            suffixes=("_resultado", "_meta")
        )
    )

    df = df[df["ano"] == df["ano_meta"]].copy()

    df = aplicar_status_meta(df)

    return (
        df
        .sort_values(["ano", "id_municipio", "rede"])
        .reset_index(drop=True)
    )


def processar_ranking_municipio_prioritario(
    df_indicador_meta_municipio: pd.DataFrame,
) -> pd.DataFrame:
    """Processa ranking de municípios prioritários."""
    df = (
        df_indicador_meta_municipio[
            df_indicador_meta_municipio["status_meta"] == "Abaixo da meta"
        ]
        .groupby(["ano", "id_municipio"])
        .agg({
            "distancia_meta": "mean",
            "taxa_alfabetizacao": "mean",
        })
        .reset_index()
        .sort_values(["ano", "distancia_meta"])
        .reset_index(drop=True)
    )
    
    df["ranking"] = df.groupby("ano").cumcount() + 1
    
    return df[df["ranking"] <= 20].reset_index(drop=True)


def processar_evolucao_alfabetizacao(
    df_fato_resultado_brasil: pd.DataFrame,
) -> pd.DataFrame:
    """Processa série histórica de evolução."""
    df = (
        df_fato_resultado_brasil
        .groupby("ano")
        .agg({
            "taxa_alfabetizacao": "mean",
            "percentual_participacao": "sum",
        })
        .reset_index()
        .sort_values("ano")
    )
    
    df["variacao_taxa"] = df["taxa_alfabetizacao"].diff()
    df["variacao_percentual"] = df["percentual_participacao"].diff()
    
    return df.reset_index(drop=True)


def processar_resumo_status_meta(
    df_indicador_meta_brasil: pd.DataFrame,
    df_indicador_meta_uf: pd.DataFrame,
    df_indicador_meta_municipio: pd.DataFrame,
) -> pd.DataFrame:
    """Processa resumo de cumprimento de metas."""
    df_brasil = (
        df_indicador_meta_brasil
        .groupby(["ano", "status_meta"])
        .size()
        .reset_index(name="quantidade")
    )
    df_brasil["nivel"] = "Brasil"
    
    df_uf = (
        df_indicador_meta_uf
        .groupby(["ano", "status_meta"])
        .size()
        .reset_index(name="quantidade")
    )
    df_uf["nivel"] = "UF"
    
    df_municipio = (
        df_indicador_meta_municipio
        .groupby(["ano", "status_meta"])
        .size()
        .reset_index(name="quantidade")
    )
    df_municipio["nivel"] = "Município"
    
    df = pd.concat(
        [df_brasil, df_uf, df_municipio],
        ignore_index=True
    )
    
    return (
        df
        .sort_values(["ano", "nivel", "status_meta"])
        .reset_index(drop=True)
    )


def processar_camada_gold() -> None:
    """
    Processa todas as análises da camada Gold.
    """
    print("Iniciando processamento da camada Gold")
    print("=" * 80)
    
    # Carregar Silver
    print("\n[CARREGAMENTO] Lendo tabelas Silver...")
    df_fato_resultado_brasil = carregar_silver("fato_resultado_brasil")
    df_fato_resultado_meta_uf = carregar_silver("fato_resultado_meta_uf")
    df_fato_resultado_meta_municipio = carregar_silver("fato_resultado_meta_municipio")
    df_fato_meta_anual_brasil = carregar_silver("fato_meta_anual_brasil")
    df_fato_meta_anual_uf = carregar_silver("fato_meta_anual_uf")
    df_fato_meta_anual_municipio = carregar_silver("fato_meta_anual_municipio")
    
    # Processar indicadores
    print("\n[PROCESSAMENTO] Gerando indicadores Gold...")
    
    df_indicador_meta_brasil = processar_indicador_meta_brasil(
        df_fato_resultado_brasil,
        df_fato_meta_anual_brasil,
    )
    salvar_gold(df_indicador_meta_brasil, "indicador_meta_brasil")
    
    df_indicador_meta_uf = processar_indicador_meta_uf(
        df_fato_resultado_meta_uf,
        df_fato_meta_anual_uf,
    )
    salvar_gold(df_indicador_meta_uf, "indicador_meta_uf")
    
    df_ranking_uf_prioritaria = processar_ranking_uf_prioritaria(
        df_indicador_meta_uf,
    )
    salvar_gold(df_ranking_uf_prioritaria, "ranking_uf_prioritaria")
    
    df_indicador_meta_municipio = processar_indicador_meta_municipio(
        df_fato_resultado_meta_municipio,
        df_fato_meta_anual_municipio,
    )
    salvar_gold(df_indicador_meta_municipio, "indicador_meta_municipio")
    
    df_ranking_municipio_prioritario = processar_ranking_municipio_prioritario(
        df_indicador_meta_municipio,
    )
    salvar_gold(df_ranking_municipio_prioritario, "ranking_municipio_prioritario")
    
    df_evolucao_alfabetizacao = processar_evolucao_alfabetizacao(
        df_fato_resultado_brasil,
    )
    salvar_gold(df_evolucao_alfabetizacao, "evolucao_alfabetizacao")
    
    df_resumo_status_meta = processar_resumo_status_meta(
        df_indicador_meta_brasil,
        df_indicador_meta_uf,
        df_indicador_meta_municipio,
    )
    salvar_gold(df_resumo_status_meta, "resumo_status_meta")
    
    print("\n" + "=" * 80)
    print("Processamento da camada Gold finalizado com sucesso!")
