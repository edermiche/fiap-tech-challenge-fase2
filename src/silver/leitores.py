from pathlib import Path

import pandas as pd


def obter_arquivo_mais_recente(caminho_tabela: Path) -> Path:
    """
    Retorna o arquivo parquet mais recente de uma entidade da camada bronze.
    """
    arquivos = list(caminho_tabela.rglob("*.parquet"))

    if not arquivos:
        raise FileNotFoundError(f"Nenhum arquivo parquet encontrado em: {caminho_tabela}")

    return max(arquivos, key=lambda arquivo: arquivo.stat().st_mtime)


def ler_entidade_bronze(caminho_tabela: Path) -> pd.DataFrame:
    """
    Le a versao parquet mais recente de uma entidade bronze.
    """
    arquivo = obter_arquivo_mais_recente(caminho_tabela)
    print(f"Lendo bronze: {arquivo}")

    return pd.read_parquet(arquivo)
