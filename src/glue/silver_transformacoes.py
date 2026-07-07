"""
Transformação Silver via AWS Glue (Python Shell).

Versão em nuvem de src/silver/processar_silver.py: baixa o pacote src/
do S3 (enviado junto com o script pelo Terraform) e executa exatamente o
mesmo processar_camada_silver() da execução local. Com LAKE_S3_BUCKET
definido, os leitores e gravadores do pipeline leem a Bronze e gravam a
Silver direto no bucket, no mesmo layout de partições
(execution_date=<data>/[ano=<ano>/]).

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

    from src.silver.processar_silver import processar_camada_silver

    processar_camada_silver()


if __name__ == "__main__":
    main()
