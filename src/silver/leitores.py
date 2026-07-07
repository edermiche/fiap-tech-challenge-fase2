# As anotações `X | None` precisam ser adiadas: o Glue Python Shell roda 3.9.
from __future__ import annotations

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


def ler_alunos_streaming(caminho_tabela: Path) -> pd.DataFrame | None:
    """
    Lê o bronze de eventos de streaming (alunos_streaming), gravado pelo
    consumer local ou pelo Lambda direto em partições ano=YYYY, sem
    execution_date. O streaming é opcional: retorna None quando ainda não
    há eventos ingeridos, e o pipeline segue apenas com o batch.
    """
    bucket = os.getenv("LAKE_S3_BUCKET")

    if bucket:
        from src.common import lake_s3

        prefixo_tabela = f"bronze/{caminho_tabela.name}"

        print(f"Lendo bronze streaming: s3://{bucket}/{prefixo_tabela}")

        try:
            return lake_s3.ler_particoes(bucket, prefixo_tabela)
        except FileNotFoundError:
            print("Nenhum evento de streaming encontrado; seguindo apenas com o batch")
            return None

    print(f"Lendo bronze streaming: {caminho_tabela}")

    try:
        return ler_particoes(caminho_tabela)
    except FileNotFoundError:
        print("Nenhum evento de streaming encontrado; seguindo apenas com o batch")
        return None
