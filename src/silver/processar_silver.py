from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd

from src.silver.config import (
    BRONZE_PATH,
    ENTIDADE_ALUNOS_STREAMING,
    ENTIDADES_BRONZE_SILVER,
)
from src.silver.gravadores import salvar_entidade_silver
from src.silver.leitores import ler_alunos_streaming, ler_entidade_bronze
from src.silver.qualidade import aplicar_qualidade_silver
from src.silver.transformacoes import transformar_bronze_para_silver


def carregar_dados_bronze() -> dict[str, pd.DataFrame]:
    dados_bronze = {}

    for entidade in ENTIDADES_BRONZE_SILVER:
        dados_bronze[entidade] = ler_entidade_bronze(BRONZE_PATH / entidade)

    df_alunos_streaming = ler_alunos_streaming(BRONZE_PATH / ENTIDADE_ALUNOS_STREAMING)

    if df_alunos_streaming is not None:
        dados_bronze[ENTIDADE_ALUNOS_STREAMING] = df_alunos_streaming

    return dados_bronze


def salvar_tabelas_silver(
    tabelas_silver: dict[str, pd.DataFrame],
    data_processamento: date,
) -> dict[str, Path | str]:
    arquivos_salvos = {}

    for nome_tabela, df in tabelas_silver.items():
        arquivos_salvos[nome_tabela] = salvar_entidade_silver(
            df,
            nome_tabela,
            data_processamento,
        )

    return arquivos_salvos


def processar_camada_silver(data_processamento: date | None = None) -> dict[str, Path | str]:
    """
    Processa as entidades bronze e materializa as tabelas da camada silver.
    """
    data_processamento = data_processamento or date.today()

    print("Iniciando processamento da camada silver")

    dados_bronze = carregar_dados_bronze()
    tabelas_silver = transformar_bronze_para_silver(dados_bronze, data_processamento)
    tabelas_silver = aplicar_qualidade_silver(tabelas_silver)
    arquivos_salvos = salvar_tabelas_silver(tabelas_silver, data_processamento)

    print("Processamento da camada silver finalizado")

    return arquivos_salvos
