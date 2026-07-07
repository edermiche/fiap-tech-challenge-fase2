"""
Utilitários de particionamento e leitura do data lake (bronze/silver/gold).

Cada tabela é gravada como execution_date=<data>/[ano=<ano>/]arquivo.parquet:
a partição por execution_date preserva o histórico de execuções do pipeline;
a partição por ano (quando a tabela tem uma coluna de ano) permite leitura
seletiva por ano, reduzindo bytes lidos em motores que fazem partition
pruning (Athena/BigQuery) — ver seção de FinOps do README. Tabelas sem
coluna de ano (dimensões/domínios) são salvas em arquivo único, sem
partição adicional.
"""
# As anotações `X | None` precisam ser adiadas: o Glue Python Shell roda 3.9.
from __future__ import annotations

from pathlib import Path

import pandas as pd

COLUNAS_ANO_CANDIDATAS = ["ano", "ano_competencia"]


def resolver_coluna_ano(df: pd.DataFrame) -> str | None:
    """Retorna a coluna de ano da tabela, se existir."""
    for coluna in COLUNAS_ANO_CANDIDATAS:
        if coluna in df.columns:
            return coluna

    return None


def salvar_particionado_por_ano(
    df: pd.DataFrame,
    caminho_base: Path,
    nome_arquivo: str,
) -> Path:
    """
    Salva um DataFrame particionado por ano dentro de caminho_base.

    Tabelas sem coluna de ano (dimensões/domínios) são salvas em um único
    arquivo direto em caminho_base, sem partição adicional.
    """
    coluna_ano = resolver_coluna_ano(df)

    if coluna_ano is None:
        caminho_base.mkdir(parents=True, exist_ok=True)
        arquivo = caminho_base / nome_arquivo
        df.to_parquet(arquivo, index=False)

        return arquivo

    for ano, df_ano in df.groupby(coluna_ano):
        pasta_ano = caminho_base / f"ano={ano}"
        pasta_ano.mkdir(parents=True, exist_ok=True)
        df_ano.to_parquet(pasta_ano / nome_arquivo, index=False)

    return caminho_base


def localizar_execution_date_mais_recente(caminho_tabela: Path) -> Path:
    """Retorna a pasta execution_date=<data> mais recente de uma tabela."""
    if not caminho_tabela.exists():
        raise FileNotFoundError(f"Pasta não encontrada: {caminho_tabela}")

    pastas = [
        pasta for pasta in caminho_tabela.iterdir()
        if pasta.is_dir() and pasta.name.startswith("execution_date=")
    ]

    if not pastas:
        raise FileNotFoundError(
            f"Nenhuma partição execution_date encontrada em: {caminho_tabela}"
        )

    return max(pastas, key=lambda pasta: pasta.name)


def ler_particoes(
    caminho_base: Path,
    colunas: list[str] | None = None,
) -> pd.DataFrame:
    """
    Lê e concatena todas as partições parquet encontradas recursivamente
    em caminho_base (todas as partições de ano de uma execução, ou o
    arquivo único de uma tabela sem partição por ano).
    """
    if not caminho_base.exists():
        raise FileNotFoundError(f"Pasta não encontrada: {caminho_base}")

    arquivos_particionados = sorted(
        arquivo
        for pasta_ano in caminho_base.glob("ano=*")
        if pasta_ano.is_dir()
        for arquivo in pasta_ano.glob("*.parquet")
    )
    arquivos = arquivos_particionados or sorted(caminho_base.glob("*.parquet"))

    if not arquivos:
        raise FileNotFoundError(f"Nenhum arquivo parquet encontrado em: {caminho_base}")

    return pd.concat(
        [pd.read_parquet(arquivo, columns=colunas) for arquivo in arquivos],
        ignore_index=True,
    )


def ler_tabela_mais_recente(
    caminho_tabela: Path,
    colunas: list[str] | None = None,
) -> pd.DataFrame:
    """
    Lê a execução mais recente de uma tabela particionada por
    execution_date, concatenando todas as suas partições de ano.
    """
    pasta_execucao = localizar_execution_date_mais_recente(caminho_tabela)

    return ler_particoes(pasta_execucao, colunas=colunas)
