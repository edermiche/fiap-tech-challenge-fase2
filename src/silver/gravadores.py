from __future__ import annotations

import os
from datetime import date
from pathlib import Path

import pandas as pd

from src.common.particionamento import salvar_particionado_por_ano
from src.silver.config import SILVER_PATH


def salvar_entidade_silver(
    df: pd.DataFrame,
    nome_tabela: str,
    data_processamento: date,
) -> Path | str:
    """
    Salva uma tabela silver em parquet, particionada por execution_date
    e, quando a tabela tem coluna de ano, por ano dentro da execução.
    Com LAKE_S3_BUCKET definido (jobs Glue), grava direto no S3.
    """
    execution_date = data_processamento.isoformat()
    bucket = os.getenv("LAKE_S3_BUCKET")

    if bucket:
        from src.common import lake_s3

        prefixo_execucao = f"silver/{nome_tabela}/execution_date={execution_date}"
        lake_s3.salvar_particionado_por_ano(
            df, bucket, prefixo_execucao, f"{nome_tabela}.parquet"
        )
        destino = f"s3://{bucket}/{prefixo_execucao}"
    else:
        caminho_execucao = SILVER_PATH / nome_tabela / f"execution_date={execution_date}"
        salvar_particionado_por_ano(df, caminho_execucao, f"{nome_tabela}.parquet")
        destino = caminho_execucao

    print(f"[OK] silver.{nome_tabela} salvo em: {destino}")
    print(f"Linhas: {len(df)} | Colunas: {len(df.columns)}")

    return destino
