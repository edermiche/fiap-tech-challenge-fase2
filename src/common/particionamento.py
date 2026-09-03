"""
Utilitários de particionamento e leitura do data lake (bronze/silver/gold).

Cada tabela é gravada como execution_date=<data>/[ano=<ano>/]arquivo.parquet:
a partição por execution_date preserva o histórico de execuções do pipeline;
a partição por ano (quando a tabela tem uma coluna de ano) permite leitura
seletiva por ano, reduzindo bytes lidos em motores que fazem partition
pruning (Athena/BigQuery) — ver seção de FinOps do README. Tabelas sem
coluna de ano (dimensões/domínios) são salvas em arquivo único, sem
partição adicional.

A coluna usada para particionar por ano não é gravada dentro do parquet:
o valor já está no nome da pasta (ano=<valor>), e mantê-la também como
coluna faz o Glue Crawler catalogar "ano" duas vezes (partição + coluna),
o que o Athena rejeita com "duplicate columns". `ler_particoes` reconstrói
essa coluna a partir do nome da pasta ao ler.
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
        df_ano.drop(columns="ano", errors="ignore").to_parquet(
            pasta_ano / nome_arquivo, index=False
        )

    return caminho_base


def listar_execution_dates(caminho_tabela: Path) -> list[Path]:
    """Pastas execution_date=<data> de uma tabela, em ordem crescente."""
    if not caminho_tabela.exists():
        raise FileNotFoundError(f"Pasta não encontrada: {caminho_tabela}")

    return sorted(
        (
            pasta for pasta in caminho_tabela.iterdir()
            if pasta.is_dir() and pasta.name.startswith("execution_date=")
        ),
        key=lambda pasta: pasta.name,
    )


def localizar_execution_date_mais_recente(caminho_tabela: Path) -> Path:
    """Retorna a pasta execution_date=<data> mais recente de uma tabela."""
    pastas = listar_execution_dates(caminho_tabela)

    if not pastas:
        raise FileNotFoundError(
            f"Nenhuma partição execution_date encontrada em: {caminho_tabela}"
        )

    return pastas[-1]


def ler_particoes(
    caminho_base: Path,
    colunas: list[str] | None = None,
) -> pd.DataFrame:
    """
    Lê e concatena todas as partições parquet encontradas recursivamente
    em caminho_base (todas as partições de ano de uma execução, ou o
    arquivo único de uma tabela sem partição por ano).

    Quando há partição por ano, a coluna não está no parquet (ver módulo);
    esta função a reconstrói a partir do nome da pasta ano=<valor>.
    """
    if not caminho_base.exists():
        raise FileNotFoundError(f"Pasta não encontrada: {caminho_base}")

    pastas_ano = sorted(pasta for pasta in caminho_base.glob("ano=*") if pasta.is_dir())

    if pastas_ano:
        incluir_ano = colunas is None or "ano" in colunas
        colunas_arquivo = [c for c in colunas if c != "ano"] if colunas else None

        frames = []
        for pasta_ano in pastas_ano:
            valor_ano = int(pasta_ano.name.split("=", 1)[1])
            for arquivo in sorted(pasta_ano.glob("*.parquet")):
                df_particao = pd.read_parquet(arquivo, columns=colunas_arquivo)
                tem_coluna_ano = any(c in df_particao.columns for c in COLUNAS_ANO_CANDIDATAS)
                if incluir_ano and not tem_coluna_ano:
                    df_particao.insert(0, "ano", valor_ano)
                frames.append(df_particao)

        return pd.concat(frames, ignore_index=True)

    arquivos = sorted(caminho_base.glob("*.parquet"))

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
