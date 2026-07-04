from pathlib import Path

import pandas as pd

from src.common.particionamento import salvar_particionado_por_ano


def salvar_entidade_bronze(df: pd.DataFrame, caminho_processado: Path, nome_arquivo: str) -> Path:
    """
    Salva a entidade processada em parquet, particionada por ano
    (quando a entidade tem coluna de ano).
    """
    return salvar_particionado_por_ano(df, caminho_processado, nome_arquivo)
