"""
Consumer serverless de eventos de avaliação de alunos (AWS Lambda).

Versão em nuvem do consumer local (consumer.py): o Lambda é acionado
automaticamente pelo Kinesis Data Streams, recebe os eventos em lote,
adiciona os metadados de ingestão e grava o resultado na camada bronze
do S3 em parquet, particionado por ano.

Fluxo equivalente ao local:

    fila local  -> Kinesis Data Streams
    consumer.py -> este handler (trigger do Kinesis)
    data/bronze/alunos_streaming/ -> s3://<bucket>/bronze/alunos_streaming/

Dependências no Lambda:
- runtime Python 3.12;
- layer gerenciada AWSSDKPandas (pandas + pyarrow);
- variável de ambiente S3_BUCKET;
- role com política AWSLambdaKinesisExecutionRole + s3:PutObject no bucket.
"""

import base64
import io
import json
import os
from datetime import datetime, timezone

import boto3
import pandas as pd

s3 = boto3.client("s3")

S3_BUCKET = os.environ["S3_BUCKET"]
PREFIXO_BRONZE_STREAMING = "bronze/alunos_streaming"


def decodificar_eventos(event: dict) -> list[dict]:
    """
    Decodifica os registros do lote do Kinesis (base64 -> JSON).
    """
    eventos = []

    for registro in event.get("Records", []):
        dados = base64.b64decode(registro["kinesis"]["data"])
        eventos.append(json.loads(dados))

    return eventos


def adicionar_metadados_streaming(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adiciona metadados técnicos de ingestão via streaming,
    espelhando o consumer local.
    """
    df = df.copy()

    df["entidade_origem"] = "alunos"
    df["modo_ingestao"] = "streaming"
    df["data_ingestao_bronze"] = datetime.now(timezone.utc).isoformat()

    return df


def gravar_eventos_s3(df: pd.DataFrame) -> list[str]:
    """
    Grava os eventos no S3 particionados por ano.

    Estrutura de saída:
    s3://<bucket>/bronze/alunos_streaming/ano=YYYY/eventos_<timestamp>.parquet
    """
    chaves_gravadas = []
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f")

    for ano, df_ano in df.groupby("ano"):
        chave = f"{PREFIXO_BRONZE_STREAMING}/ano={ano}/eventos_{timestamp}.parquet"

        buffer = io.BytesIO()
        df_ano.to_parquet(buffer, index=False)
        buffer.seek(0)

        s3.put_object(Bucket=S3_BUCKET, Key=chave, Body=buffer.getvalue())

        chaves_gravadas.append(chave)

    return chaves_gravadas


def handler(event: dict, context) -> dict:
    """
    Ponto de entrada do Lambda: processa um lote de eventos do Kinesis.
    """
    eventos = decodificar_eventos(event)

    if not eventos:
        print("Lote vazio recebido, nada a processar")
        return {"eventos_processados": 0, "arquivos_gravados": []}

    df = pd.DataFrame(eventos)
    df = adicionar_metadados_streaming(df)

    chaves = gravar_eventos_s3(df)

    print(
        f"Lote processado: {len(eventos)} eventos, "
        f"{len(chaves)} arquivo(s) gravado(s): {chaves}"
    )

    return {"eventos_processados": len(eventos), "arquivos_gravados": chaves}
