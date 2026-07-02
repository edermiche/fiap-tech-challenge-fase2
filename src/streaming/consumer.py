"""
Consumer de eventos simulados de avaliação de alunos.

Monitora continuamente a fila de micro-lotes publicados pelo producer,
processa cada lote adicionando metadados de ingestão e grava o resultado
na camada bronze em formato parquet, particionado por ano.

Em ambiente AWS, esta função equivale ao Lambda acionado pelo Kinesis:
o corpo de `processar_lote` seria o handler, e a gravação local em
data/bronze/alunos_streaming/ seria um put_object no S3.

Uso:
    python -m src.streaming.consumer
    python -m src.streaming.consumer --intervalo 1 --max-ciclos-vazios 3
"""

import argparse
import time
from datetime import datetime
from pathlib import Path

import pandas as pd

from src.streaming.config import (
    BRONZE_STREAMING_PATH,
    FILA_PATH,
    INTERVALO_CONSUMER_SEGUNDOS,
    MAX_CICLOS_VAZIOS_PADRAO,
    PROCESSADOS_PATH,
)


def listar_lotes_pendentes(fila_path: Path) -> list[Path]:
    """
    Lista os micro-lotes ainda não consumidos, em ordem de publicação.
    """
    if not fila_path.exists():
        return []

    return sorted(fila_path.glob("lote_*.json"))


def adicionar_metadados_streaming(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adiciona metadados técnicos de ingestão via streaming,
    espelhando os metadados da ingestão batch.
    """
    df = df.copy()

    df["entidade_origem"] = "alunos"
    df["modo_ingestao"] = "streaming"
    df["data_ingestao_bronze"] = datetime.now()

    return df


def gravar_eventos_bronze(df: pd.DataFrame, bronze_streaming_path: Path) -> list[Path]:
    """
    Grava os eventos na camada bronze particionados por ano.

    Estrutura de saída:
    data/bronze/alunos_streaming/ano=YYYY/eventos_<timestamp>.parquet
    """
    arquivos_gravados = []
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")

    for ano, df_ano in df.groupby("ano"):
        particao = bronze_streaming_path / f"ano={ano}"
        particao.mkdir(parents=True, exist_ok=True)

        caminho_saida = particao / f"eventos_{timestamp}.parquet"
        df_ano.to_parquet(caminho_saida, index=False)

        arquivos_gravados.append(caminho_saida)

    return arquivos_gravados


def processar_lote(caminho_lote: Path) -> int:
    """
    Processa um micro-lote: lê os eventos, adiciona metadados,
    grava na bronze e move o lote para a pasta de processados.

    Retorna a quantidade de eventos processados.
    """
    df = pd.read_json(caminho_lote, orient="records", dtype={"id_municipio": str,
                                                             "id_escola": str,
                                                             "id_aluno": str})

    df = adicionar_metadados_streaming(df)

    arquivos_gravados = gravar_eventos_bronze(df, BRONZE_STREAMING_PATH)

    for arquivo in arquivos_gravados:
        print(f"  Gravado: {arquivo}")

    PROCESSADOS_PATH.mkdir(parents=True, exist_ok=True)
    caminho_lote.rename(PROCESSADOS_PATH / caminho_lote.name)

    return len(df)


def executar_consumer(
    intervalo_segundos: float = INTERVALO_CONSUMER_SEGUNDOS,
    max_ciclos_vazios: int = MAX_CICLOS_VAZIOS_PADRAO,
) -> None:
    """
    Consome a fila continuamente até que ela permaneça vazia por
    `max_ciclos_vazios` verificações consecutivas.
    """
    print("Iniciando consumer de eventos de alfabetização")
    print(f"Fila monitorada: {FILA_PATH}")
    print(f"Saída bronze: {BRONZE_STREAMING_PATH}")

    total_eventos = 0
    total_lotes = 0
    ciclos_vazios = 0

    while ciclos_vazios < max_ciclos_vazios:
        lotes_pendentes = listar_lotes_pendentes(FILA_PATH)

        if not lotes_pendentes:
            ciclos_vazios += 1
            print(
                f"Fila vazia ({ciclos_vazios}/{max_ciclos_vazios}), "
                f"aguardando {intervalo_segundos}s..."
            )
            time.sleep(intervalo_segundos)
            continue

        ciclos_vazios = 0

        for caminho_lote in lotes_pendentes:
            print(f"Processando lote: {caminho_lote.name}")

            eventos_processados = processar_lote(caminho_lote)

            total_eventos += eventos_processados
            total_lotes += 1

    print(
        f"Consumer finalizado: {total_lotes} lotes e "
        f"{total_eventos} eventos processados"
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Consumer de eventos simulados de avaliação de alunos."
    )
    parser.add_argument(
        "--intervalo",
        type=float,
        default=INTERVALO_CONSUMER_SEGUNDOS,
        help="Intervalo em segundos entre verificações da fila.",
    )
    parser.add_argument(
        "--max-ciclos-vazios",
        type=int,
        default=MAX_CICLOS_VAZIOS_PADRAO,
        help="Quantidade de verificações vazias consecutivas antes de encerrar.",
    )

    argumentos = parser.parse_args()

    executar_consumer(
        intervalo_segundos=argumentos.intervalo,
        max_ciclos_vazios=argumentos.max_ciclos_vazios,
    )


if __name__ == "__main__":
    main()
