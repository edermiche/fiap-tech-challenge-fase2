from datetime import date
from pathlib import Path

import pandas as pd

from src.silver.config import SILVER_PATH


def salvar_entidade_silver(
    df: pd.DataFrame,
    nome_tabela: str,
    data_processamento: date,
) -> Path:
    """
    Salva uma tabela silver em parquet particionado por data de execucao.
    """
    execution_date = data_processamento.isoformat()
    caminho_saida = SILVER_PATH / nome_tabela / f"execution_date={execution_date}"
    caminho_saida.mkdir(parents=True, exist_ok=True)

    arquivo_saida = caminho_saida / f"{nome_tabela}.parquet"
    df.to_parquet(arquivo_saida, index=False)

    print(f"[OK] silver.{nome_tabela} salvo em: {arquivo_saida}")
    print(f"Linhas: {len(df)} | Colunas: {len(df.columns)}")

    return arquivo_saida
