"""
Persistência do histórico de qualidade em `gold.metricas_qualidade`.

Sem histórico, métrica de qualidade só responde "como está agora"; a
pergunta útil é comparativa ("a ausência de proficiência aumentou desde
a safra anterior?"). Por isso cada execução grava suas métricas numa
partição própria, no mesmo layout das demais tabelas do lake:

    gold/metricas_qualidade/execution_date=<data>/metricas_qualidade.parquet

A tabela não tem coluna de ano (é um log de execuções, não um fato
anual), então fica em arquivo único por execução. Local por padrão; com
LAKE_S3_BUCKET definido (jobs Glue), grava e lê direto no S3.
"""
# As anotações `X | None` precisam ser adiadas: o Glue Python Shell roda 3.9.
from __future__ import annotations

import os
from pathlib import Path

import pandas as pd

from src.common.particionamento import (
    listar_execution_dates,
    ler_particoes,
    salvar_particionado_por_ano,
)
from src.qualidade.metricas import COLUNAS_METRICAS


GOLD_PATH = Path("data/gold")
TABELA_METRICAS = "metricas_qualidade"
ARQUIVO_METRICAS = f"{TABELA_METRICAS}.parquet"


def _bucket() -> str | None:
    return os.getenv("LAKE_S3_BUCKET")


def _prefixo_tabela() -> str:
    return f"gold/{TABELA_METRICAS}"


def _caminho_execucao(data_execucao: str) -> Path:
    return GOLD_PATH / TABELA_METRICAS / f"execution_date={data_execucao}"


def listar_execucoes() -> list[str]:
    """Datas de execução já registradas, em ordem crescente."""
    bucket = _bucket()

    if bucket:
        from src.common import lake_s3

        prefixos = lake_s3.listar_execution_dates(bucket, _prefixo_tabela())

        return [prefixo.rsplit("=", 1)[-1] for prefixo in prefixos]

    caminho_tabela = GOLD_PATH / TABELA_METRICAS
    if not caminho_tabela.exists():
        return []

    return [pasta.name.split("=", 1)[1] for pasta in listar_execution_dates(caminho_tabela)]


def ler_metricas_execucao(data_execucao: str) -> pd.DataFrame | None:
    """Métricas já gravadas para uma execução, ou None se não houver."""
    bucket = _bucket()

    try:
        if bucket:
            from src.common import lake_s3

            return lake_s3.ler_particoes(
                bucket, f"{_prefixo_tabela()}/execution_date={data_execucao}"
            )

        return ler_particoes(_caminho_execucao(data_execucao))
    except FileNotFoundError:
        return None


def ler_metricas_safra_anterior(data_execucao: str) -> pd.DataFrame | None:
    """
    Métricas da execução registrada imediatamente antes de `data_execucao`.

    Ignora a própria execução corrente (reprocessamento do mesmo dia não
    é "safra anterior") e devolve None na primeira execução do lake.
    """
    anteriores = [data for data in listar_execucoes() if data < data_execucao]

    if not anteriores:
        return None

    return ler_metricas_execucao(max(anteriores))


def salvar_metricas_qualidade(
    df_metricas: pd.DataFrame,
    data_execucao: str,
) -> Path | str:
    """
    Grava as métricas na partição da execução.

    Silver e Gold gravam na mesma partição em momentos diferentes: as
    linhas já existentes das camadas presentes em `df_metricas` são
    substituídas, e as das demais camadas preservadas.
    """
    if df_metricas.empty:
        print("[QUALIDADE] nenhuma métrica para gravar")

        return _caminho_execucao(data_execucao)

    existentes = ler_metricas_execucao(data_execucao)

    if existentes is not None and not existentes.empty:
        camadas = set(df_metricas["camada"].unique())
        preservadas = existentes[~existentes["camada"].isin(camadas)]
        if not preservadas.empty:
            df_metricas = pd.concat([preservadas, df_metricas], ignore_index=True)

    # A ordem das colunas é fixada na gravação: uma partição antiga, gravada
    # antes de uma coluna nova existir, entraria no concat com o schema dela
    # e mudaria a ordem do arquivo resultante.
    df_metricas = df_metricas.reindex(columns=COLUNAS_METRICAS)

    bucket = _bucket()

    if bucket:
        from src.common import lake_s3

        prefixo = f"{_prefixo_tabela()}/execution_date={data_execucao}"
        lake_s3.salvar_particionado_por_ano(
            df_metricas, bucket, prefixo, ARQUIVO_METRICAS
        )
        destino: Path | str = f"s3://{bucket}/{prefixo}"
    else:
        destino = _caminho_execucao(data_execucao)
        salvar_particionado_por_ano(df_metricas, destino, ARQUIVO_METRICAS)

    print(
        f"[QUALIDADE] gold.{TABELA_METRICAS} atualizada "
        f"({len(df_metricas)} métricas) em: {destino}"
    )

    return destino
