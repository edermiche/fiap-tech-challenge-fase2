from pathlib import Path

import pandas as pd

from src.gold.config import SILVER_PATH


def carregar_silver(nome_tabela: str, colunas: list[str] | None = None) -> pd.DataFrame:
    """
    Le uma tabela da Silver.

    O layout atual da Silver e particionado por data de execucao:
    {tabela}/execution_date=YYYY-MM-DD/{tabela}.parquet.

    Tambem aceita layouts antigos particionados por ano, reconstruindo a
    coluna `ano`, e tabelas gravadas como arquivo unico.
    """
    caminho = SILVER_PATH / nome_tabela

    if not caminho.exists():
        raise FileNotFoundError(f"Tabela silver nao encontrada: {caminho}")

    df = _ler_layout_execution_date(caminho, nome_tabela)

    if df is None:
        df = _ler_layout_ano(caminho, nome_tabela)

    if df is None:
        df = _ler_arquivo_unico(caminho, nome_tabela)

    if colunas is not None:
        df = df[[coluna for coluna in colunas if coluna in df.columns]]

    print(f"[OK] silver.{nome_tabela} carregada")
    print(f"     Linhas: {len(df)} | Colunas: {len(df.columns)}")

    return df


def _ler_layout_execution_date(caminho: Path, nome_tabela: str) -> pd.DataFrame | None:
    particoes = sorted(caminho.glob("execution_date=*"))

    if not particoes:
        return None

    pasta_mais_recente = particoes[-1]
    arquivo = pasta_mais_recente / f"{nome_tabela}.parquet"

    if not arquivo.exists():
        raise FileNotFoundError(f"Arquivo silver nao encontrado: {arquivo}")

    print(f"Lendo silver: {arquivo}")
    return pd.read_parquet(arquivo)


def _ler_layout_ano(caminho: Path, nome_tabela: str) -> pd.DataFrame | None:
    particoes = sorted(caminho.glob("ano=*"))

    if not particoes:
        return None

    frames = []

    for pasta in particoes:
        ano_str = pasta.name.split("=", 1)[1]
        arquivo = pasta / f"{nome_tabela}.parquet"

        if not arquivo.exists():
            raise FileNotFoundError(f"Arquivo silver nao encontrado: {arquivo}")

        df_particao = pd.read_parquet(arquivo)

        if ano_str == "__null__":
            df_particao.insert(0, "ano", pd.NA)
        else:
            df_particao.insert(0, "ano", int(ano_str))

        df_particao["ano"] = df_particao["ano"].astype("Int64")
        frames.append(df_particao)

    return pd.concat(frames, ignore_index=True)


def _ler_arquivo_unico(caminho: Path, nome_tabela: str) -> pd.DataFrame:
    arquivo = caminho / f"{nome_tabela}.parquet"

    if not arquivo.exists():
        raise FileNotFoundError(f"Arquivo silver nao encontrado: {arquivo}")

    print(f"Lendo silver: {arquivo}")
    return pd.read_parquet(arquivo)
