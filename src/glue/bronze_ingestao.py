"""
Ingestão Bronze via AWS Glue (Python Shell).

Versão em nuvem de src/bronze/download_bigquery.py: consulta a Base dos
Dados no BigQuery autenticando com uma service account guardada no
Secrets Manager e grava as tabelas em parquet no S3, particionadas por
execution_date — mesmo layout da execução local.

O mesmo dry run de custo e a mesma trava maximum_bytes_billed da versão
local são aplicados antes de cada consulta.

Argumentos do job (definidos em default_arguments no Terraform):
    --S3_BUCKET         bucket do data lake
    --GCP_SECRET_NAME   secret com o JSON da service account GCP
    --MAX_BYTES_BILLED  trava de custo por consulta (bytes)
    --QUERIES_PREFIX    prefixo S3 onde estão os arquivos .sql
"""

import io
import json
import sys
from datetime import datetime, timezone

import boto3
import pandas as pd
from awsglue.utils import getResolvedOptions
from botocore.exceptions import ClientError

SCOPES = ["https://www.googleapis.com/auth/bigquery"]

PREFIXO_BRONZE = "bronze"

TABELAS = [
    "uf",
    "meta_alfabetizacao_brasil",
    "meta_alfabetizacao_uf",
    "meta_alfabetizacao_municipio",
    "municipio",
    "alunos",
    "bolsa_familia_municipio",
]

s3 = boto3.client("s3")


def obter_credenciais(secret_name: str):
    """
    Monta as credenciais Google a partir da service account
    guardada no Secrets Manager. Retorna (credenciais, project_id).
    """
    from google.oauth2 import service_account

    secretsmanager = boto3.client("secretsmanager")
    resposta = secretsmanager.get_secret_value(SecretId=secret_name)
    info = json.loads(resposta["SecretString"])

    credenciais = service_account.Credentials.from_service_account_info(
        info, scopes=SCOPES
    )

    print(f"Autenticado via service account: {info.get('client_email')}")

    return credenciais, info["project_id"]


def carregar_query(bucket: str, queries_prefix: str, nome_tabela: str) -> str:
    """
    Lê o arquivo .sql da tabela a partir do S3 (enviado junto com o
    script pelo Terraform).
    """
    chave = f"{queries_prefix}/{nome_tabela}.sql"
    objeto = s3.get_object(Bucket=bucket, Key=chave)

    return objeto["Body"].read().decode("utf-8")


def estimar_consultas(client, bucket: str, queries_prefix: str, tabelas: list) -> pd.DataFrame:
    """
    Executa dry run de cada consulta para estimar o volume processado,
    sem custo e sem baixar dados.
    """
    from google.cloud import bigquery

    estimativas = []

    for nome_tabela in tabelas:
        query = carregar_query(bucket, queries_prefix, nome_tabela)

        job_config = bigquery.QueryJobConfig(dry_run=True, use_query_cache=False)
        dry_run_job = client.query(query, job_config=job_config)

        # Algumas tabelas não reportam bytes no dry run (mesma guarda da
        # versão local); o custo real segue travado por maximum_bytes_billed.
        bytes_processados = dry_run_job.total_bytes_processed
        mb_estimados = (
            round(bytes_processados / 1024 / 1024, 2)
            if bytes_processados is not None
            else None
        )

        estimativas.append(
            {
                "tabela": nome_tabela,
                "mb_estimados": mb_estimados,
            }
        )

    return pd.DataFrame(estimativas)


def objeto_existe(bucket: str, chave: str) -> bool:
    try:
        s3.head_object(Bucket=bucket, Key=chave)
        return True
    except ClientError as erro:
        if erro.response["Error"]["Code"] in ("404", "NoSuchKey", "NotFound"):
            return False
        raise


def baixar_tabela(
    client,
    bucket: str,
    queries_prefix: str,
    nome_tabela: str,
    max_bytes_billed: int,
    execution_date: str,
) -> dict:
    """
    Baixa uma tabela do BigQuery e salva na Bronze do S3 em parquet.

    Se o objeto da execution_date já existir, a consulta não é
    executada novamente (mesmo cache de resultados da versão local).
    """
    from google.cloud import bigquery

    chave_saida = (
        f"{PREFIXO_BRONZE}/{nome_tabela}/"
        f"execution_date={execution_date}/{nome_tabela}.parquet"
    )

    if objeto_existe(bucket, chave_saida):
        print(f"[SKIP] {nome_tabela}: objeto já existe (s3://{bucket}/{chave_saida})")
        return {"tabela": nome_tabela, "status": "ja_existia", "linhas": None}

    print(f"[RUN] {nome_tabela}: executando consulta...")

    job_config = bigquery.QueryJobConfig(
        maximum_bytes_billed=max_bytes_billed,
        use_query_cache=True,
    )

    query_job = client.query(
        carregar_query(bucket, queries_prefix, nome_tabela), job_config=job_config
    )
    df = query_job.to_dataframe()

    buffer = io.BytesIO()
    df.to_parquet(buffer, index=False)
    buffer.seek(0)

    s3.put_object(Bucket=bucket, Key=chave_saida, Body=buffer.getvalue())

    print(f"[OK] {nome_tabela}: {len(df)} linhas salvas em s3://{bucket}/{chave_saida}")

    return {"tabela": nome_tabela, "status": "baixado", "linhas": len(df)}


def main() -> None:
    argumentos = getResolvedOptions(
        sys.argv,
        ["S3_BUCKET", "GCP_SECRET_NAME", "MAX_BYTES_BILLED", "QUERIES_PREFIX"],
    )

    bucket = argumentos["S3_BUCKET"]
    queries_prefix = argumentos["QUERIES_PREFIX"].strip("/")
    max_bytes_billed = int(argumentos["MAX_BYTES_BILLED"])

    from google.cloud import bigquery

    credenciais, project_id = obter_credenciais(argumentos["GCP_SECRET_NAME"])
    client = bigquery.Client(project=project_id, credentials=credenciais)

    print(f"Projeto GCP: {project_id}")
    print(f"Bucket destino: {bucket}")
    print(f"Limite por consulta: {max_bytes_billed / 1024 / 1024:.0f} MB")

    print("\nEstimativa de volume (dry run):")
    df_estimativas = estimar_consultas(client, bucket, queries_prefix, TABELAS)
    print(df_estimativas.to_string(index=False))

    execution_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    print("\nIniciando download:")
    resultados = [
        baixar_tabela(
            client, bucket, queries_prefix, tabela, max_bytes_billed, execution_date
        )
        for tabela in TABELAS
    ]

    print("\nResumo:")
    print(pd.DataFrame(resultados).to_string(index=False))


if __name__ == "__main__":
    main()
