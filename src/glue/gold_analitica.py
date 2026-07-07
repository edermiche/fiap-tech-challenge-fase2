"""
Camada Gold analítica via AWS Glue (Python Shell).

Versão em nuvem de src/gold/processar_gold.py: baixa o pacote src/ do S3
(enviado junto com o script pelo Terraform) e executa exatamente o mesmo
processar_camada_gold() da execução local. Com LAKE_S3_BUCKET definido,
as tabelas Silver são lidas e as tabelas Gold gravadas direto no bucket,
no mesmo layout de partições (execution_date=<data>/[ano=<ano>/]).

Argumentos do job (definidos em default_arguments no Terraform):
    --S3_BUCKET     bucket do data lake
    --SRC_ZIP_KEY   chave S3 do zip com o pacote src/
"""

import io
import os
import sys
import tempfile
import zipfile

import boto3
from awsglue.utils import getResolvedOptions


def preparar_pacote_src(bucket: str, chave_zip: str) -> None:
    """Baixa e extrai o pacote src/ do S3, deixando-o importável."""
    corpo = boto3.client("s3").get_object(Bucket=bucket, Key=chave_zip)["Body"].read()

    destino = tempfile.mkdtemp(prefix="pipeline-")

    with zipfile.ZipFile(io.BytesIO(corpo)) as pacote:
        pacote.extractall(os.path.join(destino, "src"))

    sys.path.insert(0, destino)

    print(f"Pacote src/ extraído de s3://{bucket}/{chave_zip}")


def main() -> None:
    argumentos = getResolvedOptions(sys.argv, ["S3_BUCKET", "SRC_ZIP_KEY"])

    os.environ["LAKE_S3_BUCKET"] = argumentos["S3_BUCKET"]
    preparar_pacote_src(argumentos["S3_BUCKET"], argumentos["SRC_ZIP_KEY"])

    from src.gold.processar_gold import processar_camada_gold

    processar_camada_gold()


if __name__ == "__main__":
    main()
