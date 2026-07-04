from pathlib import Path

import pandas as pd

from src.common.particionamento import ler_particoes


def ler_entidade_bronze(caminho_tabela: Path) -> pd.DataFrame:
    """
    Lê todas as partições de ano do bronze processado de uma entidade.
    """
    caminho_processado = caminho_tabela / "processado"

    print(f"Lendo bronze: {caminho_processado}")

    return ler_particoes(caminho_processado)
