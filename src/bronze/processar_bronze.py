from datetime import datetime

import pandas as pd

from src.bronze.config import BRONZE_PATH, ENTIDADES_BRONZE
from src.bronze.leitores import ler_entidade_bronze
from src.bronze.gravadores import salvar_entidade_bronze


def adicionar_metadados_bronze(df: pd.DataFrame, entidade: str) -> pd.DataFrame:
    """
    Adiciona metadados técnicos de ingestão na camada bronze.

    Neste momento o fluxo está simulando uma ingestão batch.
    No futuro, a coluna modo_ingestao poderá receber outros valores,
    como streaming.
    """
    df = df.copy()

    df["entidade_origem"] = entidade
    df["modo_ingestao"] = "batch"
    df["data_ingestao_bronze"] = datetime.now()

    return df


def processar_entidade_bronze(entidade: str) -> None:
    """
    Processa uma entidade da camada bronze.
    """
    caminho_entidade = BRONZE_PATH / entidade
    caminho_saida = BRONZE_PATH / entidade / f"{entidade}_processado.parquet"

    print(f"Processando entidade: {entidade}")

    df = ler_entidade_bronze(caminho_entidade)
    df = adicionar_metadados_bronze(df, entidade)

    salvar_entidade_bronze(df, caminho_saida)

    print(f"Entidade processada: {entidade}")
    print(f"Arquivo salvo em: {caminho_saida}")


def processar_camada_bronze() -> None:
    """
    Processa todas as entidades configuradas na camada bronze.
    """
    print("Iniciando processamento da camada bronze")

    for entidade in ENTIDADES_BRONZE:
        processar_entidade_bronze(entidade)

    print("Processamento da camada bronze finalizado")