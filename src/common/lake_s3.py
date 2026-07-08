"""
Utilitários de particionamento e leitura do data lake no S3.

Espelho de src/common/particionamento.py para a execução em nuvem (jobs
Glue): mesmas convenções de layout — cada tabela gravada como
execution_date=<data>/[ano=<ano>/]arquivo.parquet — trocando o sistema
de arquivos local pelo bucket do data lake. Os leitores e gravadores do
pipeline usam este módulo quando a variável de ambiente LAKE_S3_BUCKET
está definida.

Assim como no espelho local, a coluna de ano não é gravada dentro do
parquet quando ela também é a partição (ver particionamento.py) — evita
coluna duplicada no Glue Catalog/Athena.
"""
from __future__ import annotations

import io

import pandas as pd

from src.common.particionamento import resolver_coluna_ano

_cliente_s3 = None


def cliente_s3():
    """Cliente S3 criado sob demanda, para não exigir boto3/credenciais fora da nuvem."""
    global _cliente_s3

    if _cliente_s3 is None:
        import boto3

        _cliente_s3 = boto3.client("s3")

    return _cliente_s3


def listar_chaves_parquet(bucket: str, prefixo: str) -> list[str]:
    """Lista recursivamente as chaves .parquet sob um prefixo."""
    paginador = cliente_s3().get_paginator("list_objects_v2")

    return sorted(
        objeto["Key"]
        for pagina in paginador.paginate(
            Bucket=bucket, Prefix=f"{prefixo.rstrip('/')}/"
        )
        for objeto in pagina.get("Contents", [])
        if objeto["Key"].endswith(".parquet")
    )


def localizar_execution_date_mais_recente(bucket: str, prefixo_tabela: str) -> str:
    """Retorna o prefixo execution_date=<data> mais recente de uma tabela."""
    prefixo_tabela = prefixo_tabela.rstrip("/")
    paginador = cliente_s3().get_paginator("list_objects_v2")

    particoes = [
        comum["Prefix"].rstrip("/")
        for pagina in paginador.paginate(
            Bucket=bucket, Prefix=f"{prefixo_tabela}/", Delimiter="/"
        )
        for comum in pagina.get("CommonPrefixes", [])
        if comum["Prefix"].rstrip("/").rsplit("/", 1)[-1].startswith("execution_date=")
    ]

    if not particoes:
        raise FileNotFoundError(
            f"Nenhuma partição execution_date encontrada em: s3://{bucket}/{prefixo_tabela}"
        )

    return max(particoes)


def ler_particoes(
    bucket: str,
    prefixo: str,
    colunas: list[str] | None = None,
) -> pd.DataFrame:
    """
    Lê e concatena todas as partições parquet encontradas recursivamente
    sob um prefixo (todas as partições de ano de uma execução, ou o
    arquivo único de uma tabela sem partição por ano).

    Quando há partição por ano, a coluna não está no parquet (ver módulo);
    esta função a reconstrói a partir do segmento ano=<valor> da chave.
    """
    chaves = listar_chaves_parquet(bucket, prefixo)

    if not chaves:
        raise FileNotFoundError(
            f"Nenhum arquivo parquet encontrado em: s3://{bucket}/{prefixo}"
        )

    incluir_ano = colunas is None or "ano" in colunas
    colunas_arquivo = [c for c in colunas if c != "ano"] if colunas else None

    frames = []
    for chave in chaves:
        df_particao = _ler_parquet(bucket, chave, colunas_arquivo)
        valor_ano = _extrair_particao_ano(chave)

        if incluir_ano and valor_ano is not None and "ano" not in df_particao.columns:
            df_particao.insert(0, "ano", valor_ano)

        frames.append(df_particao)

    return pd.concat(frames, ignore_index=True)


def _extrair_particao_ano(chave: str) -> int | None:
    """Extrai o valor de ano do segmento ano=<valor> de uma chave S3, se houver."""
    for segmento in chave.split("/"):
        if segmento.startswith("ano="):
            return int(segmento.split("=", 1)[1])

    return None


def ler_tabela_mais_recente(
    bucket: str,
    prefixo_tabela: str,
    colunas: list[str] | None = None,
) -> pd.DataFrame:
    """
    Lê a execução mais recente de uma tabela particionada por
    execution_date, concatenando todas as suas partições de ano.
    """
    prefixo_execucao = localizar_execution_date_mais_recente(bucket, prefixo_tabela)

    return ler_particoes(bucket, prefixo_execucao, colunas=colunas)


def salvar_particionado_por_ano(
    df: pd.DataFrame,
    bucket: str,
    prefixo_base: str,
    nome_arquivo: str,
) -> str:
    """
    Salva um DataFrame particionado por ano dentro de prefixo_base.

    Tabelas sem coluna de ano (dimensões/domínios) são salvas em um único
    objeto direto em prefixo_base, sem partição adicional.
    """
    prefixo_base = prefixo_base.rstrip("/")
    coluna_ano = resolver_coluna_ano(df)

    if coluna_ano is None:
        chave = f"{prefixo_base}/{nome_arquivo}"
        _gravar_parquet(df, bucket, chave)

        return chave

    for ano, df_ano in df.groupby(coluna_ano):
        _gravar_parquet(
            df_ano.drop(columns="ano", errors="ignore"),
            bucket,
            f"{prefixo_base}/ano={ano}/{nome_arquivo}",
        )

    return prefixo_base


def _ler_parquet(bucket: str, chave: str, colunas: list[str] | None = None) -> pd.DataFrame:
    corpo = cliente_s3().get_object(Bucket=bucket, Key=chave)["Body"].read()

    return pd.read_parquet(io.BytesIO(corpo), columns=colunas)


def _gravar_parquet(df: pd.DataFrame, bucket: str, chave: str) -> None:
    buffer = io.BytesIO()
    df.to_parquet(buffer, index=False)
    cliente_s3().put_object(Bucket=bucket, Key=chave, Body=buffer.getvalue())
