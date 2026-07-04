from datetime import date
from pathlib import Path

import pandas as pd

from src.common.particionamento import salvar_particionado_por_ano
from src.silver.config import SILVER_PATH


def salvar_entidade_silver(
    df: pd.DataFrame,
    nome_tabela: str,
    data_processamento: date,
) -> Path:
    """
    Salva uma tabela silver em parquet, particionada por execution_date
    e, quando a tabela tem coluna de ano, por ano dentro da execução.
    """
    execution_date = data_processamento.isoformat()
    caminho_execucao = SILVER_PATH / nome_tabela / f"execution_date={execution_date}"

    salvar_particionado_por_ano(df, caminho_execucao, f"{nome_tabela}.parquet")

    print(f"[OK] silver.{nome_tabela} salvo em: {caminho_execucao}")
    print(f"Linhas: {len(df)} | Colunas: {len(df.columns)}")

    return caminho_execucao
