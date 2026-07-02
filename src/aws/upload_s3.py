"""
Upload do data lake local para o S3.

Sobe as camadas bronze, silver e gold de data/ para o bucket configurado,
preservando a estrutura de pastas e partições (execution_date, ano).

O nome do bucket e a região vêm do arquivo .env, para que nenhum
identificador de conta fique fixo no código.

Uso:
    python -m src.aws.upload_s3
    python -m src.aws.upload_s3 --camadas bronze
    python -m src.aws.upload_s3 --dry-run
"""

import argparse
import os
from pathlib import Path

import boto3
from dotenv import load_dotenv

DATA_PATH = Path("data")

CAMADAS_PADRAO = ["bronze", "silver", "gold"]


def listar_arquivos_camada(camada: str) -> list[Path]:
    """
    Lista os arquivos parquet da camada, ignorando artefatos de controle.
    """
    caminho_camada = DATA_PATH / camada

    if not caminho_camada.exists():
        return []

    return [
        arquivo
        for arquivo in caminho_camada.rglob("*.parquet")
        if arquivo.is_file()
    ]


def montar_chave_s3(arquivo: Path) -> str:
    """
    Converte o caminho local em chave S3, preservando a estrutura.

    data/bronze/alunos/execution_date=2026-07-02/alunos.parquet
    -> bronze/alunos/execution_date=2026-07-02/alunos.parquet
    """
    return arquivo.relative_to(DATA_PATH).as_posix()


def enviar_camada(client, bucket: str, camada: str, dry_run: bool) -> int:
    """
    Envia todos os arquivos de uma camada ao bucket.

    Retorna a quantidade de arquivos enviados.
    """
    arquivos = listar_arquivos_camada(camada)

    if not arquivos:
        print(f"[AVISO] Camada {camada}: nenhum arquivo parquet encontrado, pulando")
        return 0

    print(f"Camada {camada}: {len(arquivos)} arquivo(s)")

    for arquivo in arquivos:
        chave = montar_chave_s3(arquivo)
        tamanho_mb = arquivo.stat().st_size / 1024 / 1024

        if dry_run:
            print(f"  [DRY-RUN] {chave} ({tamanho_mb:.2f} MB)")
            continue

        client.upload_file(str(arquivo), bucket, chave)
        print(f"  [OK] s3://{bucket}/{chave} ({tamanho_mb:.2f} MB)")

    return len(arquivos)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Upload do data lake local para o S3."
    )
    parser.add_argument(
        "--camadas",
        nargs="+",
        default=CAMADAS_PADRAO,
        choices=CAMADAS_PADRAO,
        help="Camadas a enviar (padrão: todas).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Apenas lista o que seria enviado, sem subir arquivos.",
    )

    argumentos = parser.parse_args()

    load_dotenv()

    bucket = os.getenv("S3_BUCKET")
    regiao = os.getenv("AWS_REGION", "sa-east-1")

    if not bucket:
        raise ValueError(
            "S3_BUCKET não encontrado. "
            "Preencha o nome do bucket no arquivo .env."
        )

    client = boto3.client("s3", region_name=regiao)

    print(f"Bucket destino: s3://{bucket} ({regiao})")

    total = 0

    for camada in argumentos.camadas:
        total += enviar_camada(client, bucket, camada, argumentos.dry_run)

    acao = "listados" if argumentos.dry_run else "enviados"
    print(f"\nUpload finalizado: {total} arquivo(s) {acao}")


if __name__ == "__main__":
    main()
