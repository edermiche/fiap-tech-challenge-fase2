from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd

from src.qualidade.armazenamento import (
    ler_metricas_safra_anterior,
    salvar_metricas_qualidade,
)
from src.qualidade.metricas import (
    avaliar_gates,
    coletar_metricas_silver,
    comparar_com_safra_anterior,
    imprimir_resumo,
)
from src.silver.config import (
    BRONZE_PATH,
    ENTIDADE_ALUNOS_STREAMING,
    ENTIDADES_BRONZE_SILVER,
)
from src.silver.gravadores import salvar_entidade_silver
from src.silver.leitores import ler_alunos_streaming, ler_entidade_bronze
from src.silver.qualidade import aplicar_qualidade_silver, relatorio_ausencia_fonte
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


def registrar_qualidade_silver(
    tabelas_silver: dict[str, pd.DataFrame],
    volumetria_limpeza: dict[str, tuple[int, int, int]],
    data_processamento: date,
) -> pd.DataFrame:
    """
    Mede a qualidade da Silver, grava o resultado em
    gold.metricas_qualidade e aplica o gate.

    A ordem importa: as métricas são persistidas **antes** do gate, para
    que uma execução barrada também deixe rastro auditável; e o gate roda
    **antes** da gravação das tabelas, para que uma safra reprovada não
    seja publicada nem chegue à Gold.
    """
    data_execucao = data_processamento.isoformat()

    df_metricas = coletar_metricas_silver(
        tabelas_silver,
        volumetria_limpeza,
        data_execucao,
    )
    df_metricas = comparar_com_safra_anterior(
        df_metricas,
        ler_metricas_safra_anterior(data_execucao),
    )

    salvar_metricas_qualidade(df_metricas, data_execucao)
    imprimir_resumo(df_metricas)
    avaliar_gates(df_metricas)

    return df_metricas


def processar_camada_silver(data_processamento: date | None = None) -> dict[str, Path | str]:
    """
    Processa as entidades bronze e materializa as tabelas da camada silver.
    """
    data_processamento = data_processamento or date.today()

    print("Iniciando processamento da camada silver")

    dados_bronze = carregar_dados_bronze()
    tabelas_silver = transformar_bronze_para_silver(dados_bronze, data_processamento)
    tabelas_silver, volumetria_limpeza = aplicar_qualidade_silver(tabelas_silver)
    relatorio_ausencia_fonte(tabelas_silver)
    registrar_qualidade_silver(tabelas_silver, volumetria_limpeza, data_processamento)
    arquivos_salvos = salvar_tabelas_silver(tabelas_silver, data_processamento)

    print("Processamento da camada silver finalizado")

    return arquivos_salvos
