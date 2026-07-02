"""
Producer de eventos simulados de avaliação de alunos.

Lê a base consolidada da camada bronze e reemite os registros como
eventos incrementais em micro-lotes, simulando a chegada contínua de
novas medições de desempenho.

Nesta simulação local, publicar um micro-lote significa gravar um
arquivo JSON no diretório de fila. Em ambiente AWS, a única mudança
é o destino: em vez de gravar em disco, o lote seria enviado ao
Kinesis Data Streams via boto3 (put_records).

Uso:
    python -m src.streaming.producer
    python -m src.streaming.producer --total-eventos 500 --tamanho-lote 50
"""

import argparse
import time
from datetime import datetime
from pathlib import Path

import pandas as pd

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


def executar_producer(
    total_eventos: int = TOTAL_EVENTOS_PADRAO,
    tamanho_lote: int = TAMANHO_LOTE_PADRAO,
    intervalo_segundos: float = INTERVALO_PRODUCER_SEGUNDOS,
    caminho_fonte: Path = ARQUIVO_FONTE_EVENTOS,
) -> None:
    """
    Emite eventos em micro-lotes até atingir o total configurado.
    """
    print("Iniciando producer de eventos de alfabetização")
    print(f"Fonte: {caminho_fonte}")
    print(f"Total de eventos: {total_eventos} | Tamanho do lote: {tamanho_lote}")

    df_eventos = carregar_eventos_fonte(caminho_fonte, total_eventos)

    FILA_PATH.mkdir(parents=True, exist_ok=True)

    total_publicado = 0

    for numero_lote, inicio in enumerate(range(0, len(df_eventos), tamanho_lote), start=1):
        df_lote = df_eventos.iloc[inicio : inicio + tamanho_lote]

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

    argumentos = parser.parse_args()

    executar_producer(
        total_eventos=argumentos.total_eventos,
        tamanho_lote=argumentos.tamanho_lote,
        intervalo_segundos=argumentos.intervalo,
        caminho_fonte=argumentos.fonte,
    )


if __name__ == "__main__":
    main()
