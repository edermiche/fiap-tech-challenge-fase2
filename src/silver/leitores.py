import os
from pathlib import Path

import pandas as pd

from src.common.particionamento import ler_particoes


def ler_entidade_bronze(caminho_tabela: Path) -> pd.DataFrame:
    """
    Lê o bronze de uma entidade: localmente, todas as partições de ano do
    bronze processado; com LAKE_S3_BUCKET definido (jobs Glue), a execução
    mais recente gravada pela ingestão bronze direto no S3.
    """
    bucket = os.getenv("LAKE_S3_BUCKET")

    if bucket:
        from src.common import lake_s3

        prefixo_tabela = f"bronze/{caminho_tabela.name}"

        print(f"Lendo bronze: s3://{bucket}/{prefixo_tabela}")

        return lake_s3.ler_tabela_mais_recente(bucket, prefixo_tabela)

    caminho_processado = caminho_tabela / "processado"

    print(f"Lendo bronze: {caminho_processado}")

    return ler_particoes(caminho_processado)
