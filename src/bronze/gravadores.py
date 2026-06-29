from pathlib import Path

import pandas as pd


def salvar_entidade_bronze(df: pd.DataFrame, caminho_saida: Path) -> None:
    """
    Salva a entidade processada em formato parquet.
    """
    caminho_saida.parent.mkdir(parents=True, exist_ok=True)

    df.to_parquet(
        caminho_saida,
        index=False
    )