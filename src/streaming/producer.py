"""
Producer de eventos simulados de avaliação de alunos.

Lê a base consolidada da camada bronze e reemite os registros como
eventos incrementais em micro-lotes, simulando a chegada contínua de
novas medições de desempenho.

Suporta dois destinos:

- local (padrão): grava micro-lotes JSON no diretório de fila,
  permitindo executar a simulação sem conta AWS;
- kinesis: envia os mesmos micro-lotes ao Kinesis Data Streams
  via put_records, usando o stream configurado no .env.

Uso:
    python -m src.streaming.producer
    python -m src.streaming.producer --total-eventos 500 --tamanho-lote 50
    python -m src.streaming.producer --destino kinesis
"""

import argparse
import json
import time
from datetime import datetime
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

from src.streaming.config import (
    ARQUIVO_FONTE_EVENTOS,
    COLUNAS_METADADOS_BATCH,
    FILA_PATH,
    INTERVALO_PRODUCER_SEGUNDOS,
    TAMANHO_LOTE_PADRAO,
    TOTAL_EVENTOS_PADRAO,
)


def carregar_eventos_fonte(caminho_fonte: Path, total_eventos: int) -> pd.DataFrame:
    """
    Carrega os registros que serão reemitidos como eventos.

    Remove as colunas de metadados do pipeline batch para que o evento
    represente apenas o dado "cru" da medição.
    """
    if not caminho_fonte.exists():
        raise FileNotFoundError(
            f"Arquivo fonte não encontrado: {caminho_fonte}. "
            "Execute primeiro o pipeline bronze (python main.py)."
        )

    df = pd.read_parquet(caminho_fonte)

    colunas_para_remover = [
        coluna for coluna in COLUNAS_METADADOS_BATCH if coluna in df.columns
    ]
    df = df.drop(columns=colunas_para_remover)

    return df.head(total_eventos)


def publicar_lote(df_lote: pd.DataFrame, fila_path: Path, numero_lote: int) -> Path:
    """
    Publica um micro-lote de eventos na fila.

    O arquivo é gravado com extensão temporária e depois renomeado,
    para que o consumer nunca leia um lote parcialmente escrito.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    caminho_final = fila_path / f"lote_{timestamp}_{numero_lote:05d}.json"
    caminho_temporario = caminho_final.with_suffix(".tmp")

    df_lote.to_json(
        caminho_temporario,
        orient="records",
        force_ascii=False,
        date_format="iso",
    )

    caminho_temporario.rename(caminho_final)

    return caminho_final


def publicar_lote_kinesis(client, df_lote: pd.DataFrame, stream_name: str) -> int:
    """
    Publica um micro-lote de eventos no Kinesis Data Streams.

    Cada registro vira um evento JSON individual no stream. A chave de
    partição é o id_municipio, mantendo eventos do mesmo município no
    mesmo shard (ordem preservada por município).
    """
    # NaN não é JSON válido; converte para None (null) antes da serialização
    df_lote = df_lote.astype(object).where(pd.notna(df_lote), None)

    registros = [
        {
            "Data": json.dumps(evento, ensure_ascii=False, default=str).encode("utf-8"),
            "PartitionKey": str(evento.get("id_municipio", "sem_municipio")),
        }
        for evento in df_lote.to_dict(orient="records")
    ]

    resposta = client.put_records(StreamName=stream_name, Records=registros)

    falhas = resposta.get("FailedRecordCount", 0)

    if falhas:
        print(f"  [AVISO] {falhas} registro(s) falharam no envio")

    return len(registros) - falhas


def executar_producer(
    total_eventos: int = TOTAL_EVENTOS_PADRAO,
    tamanho_lote: int = TAMANHO_LOTE_PADRAO,
    intervalo_segundos: float = INTERVALO_PRODUCER_SEGUNDOS,
    caminho_fonte: Path = ARQUIVO_FONTE_EVENTOS,
    destino: str = "local",
) -> None:
    """
    Emite eventos em micro-lotes até atingir o total configurado.
    """
    print("Iniciando producer de eventos de alfabetização")
    print(f"Fonte: {caminho_fonte}")
    print(f"Destino: {destino}")
    print(f"Total de eventos: {total_eventos} | Tamanho do lote: {tamanho_lote}")

    df_eventos = carregar_eventos_fonte(caminho_fonte, total_eventos)

    client_kinesis = None
    stream_name = None

    if destino == "kinesis":
        import os

        import boto3

        from src.streaming.config import KINESIS_STREAM_NAME

        stream_name = KINESIS_STREAM_NAME
        regiao = os.getenv("AWS_REGION", "sa-east-1")
        client_kinesis = boto3.client("kinesis", region_name=regiao)

        print(f"Stream: {stream_name} ({regiao})")
    else:
        FILA_PATH.mkdir(parents=True, exist_ok=True)

    total_publicado = 0

    for numero_lote, inicio in enumerate(range(0, len(df_eventos), tamanho_lote), start=1):
        df_lote = df_eventos.iloc[inicio : inicio + tamanho_lote]

        if destino == "kinesis":
            enviados = publicar_lote_kinesis(client_kinesis, df_lote, stream_name)
            total_publicado += enviados

            print(
                f"Lote {numero_lote} publicado no Kinesis: {enviados} eventos "
                f"({total_publicado}/{len(df_eventos)})"
            )
        else:
            caminho_lote = publicar_lote(df_lote, FILA_PATH, numero_lote)
            total_publicado += len(df_lote)

            print(
                f"Lote {numero_lote} publicado: {len(df_lote)} eventos "
                f"({total_publicado}/{len(df_eventos)}) -> {caminho_lote.name}"
            )

        time.sleep(intervalo_segundos)

    print(f"Producer finalizado: {total_publicado} eventos publicados")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Producer de eventos simulados de avaliação de alunos."
    )
    parser.add_argument(
        "--total-eventos",
        type=int,
        default=TOTAL_EVENTOS_PADRAO,
        help="Quantidade total de eventos a publicar.",
    )
    parser.add_argument(
        "--tamanho-lote",
        type=int,
        default=TAMANHO_LOTE_PADRAO,
        help="Quantidade de eventos por micro-lote.",
    )
    parser.add_argument(
        "--intervalo",
        type=float,
        default=INTERVALO_PRODUCER_SEGUNDOS,
        help="Intervalo em segundos entre micro-lotes.",
    )
    parser.add_argument(
        "--fonte",
        type=Path,
        default=ARQUIVO_FONTE_EVENTOS,
        help="Arquivo parquet usado como fonte dos eventos.",
    )
    parser.add_argument(
        "--destino",
        choices=["local", "kinesis"],
        default="local",
        help="Destino dos eventos: fila local (padrão) ou Kinesis Data Streams.",
    )

    argumentos = parser.parse_args()

    load_dotenv()

    executar_producer(
        total_eventos=argumentos.total_eventos,
        tamanho_lote=argumentos.tamanho_lote,
        intervalo_segundos=argumentos.intervalo,
        caminho_fonte=argumentos.fonte,
        destino=argumentos.destino,
    )


if __name__ == "__main__":
    main()
