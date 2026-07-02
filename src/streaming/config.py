from pathlib import Path


# Fonte dos eventos simulados: saída consolidada da camada bronze batch.
# O producer lê este arquivo e reemite os registros como eventos incrementais.
ARQUIVO_FONTE_EVENTOS = Path("data/bronze/alunos/alunos_processado.parquet")

# Diretório que simula o stream de eventos.
# Em ambiente AWS, este diretório equivale ao Kinesis Data Stream:
# cada arquivo JSON gravado aqui representa um micro-lote de eventos
# publicado no stream (PutRecords).
FILA_PATH = Path("data/streaming/fila")

# Diretório para onde os micro-lotes já consumidos são movidos.
# No Kinesis não existe este conceito (o stream retém os eventos por TTL);
# aqui ele evita que o consumer reprocesse o mesmo lote.
PROCESSADOS_PATH = Path("data/streaming/processados")

# Saída bronze dos eventos recebidos via streaming, separada da entidade
# "alunos" (batch) para não misturar os dois modos de ingestão.
# Em ambiente AWS, equivale ao prefixo S3 onde o Lambda consumer grava.
BRONZE_STREAMING_PATH = Path("data/bronze/alunos_streaming")


# Parâmetros padrão da simulação
TOTAL_EVENTOS_PADRAO = 1000
TAMANHO_LOTE_PADRAO = 100
INTERVALO_PRODUCER_SEGUNDOS = 1.0
INTERVALO_CONSUMER_SEGUNDOS = 2.0
MAX_CICLOS_VAZIOS_PADRAO = 5

# Nome do Kinesis Data Stream usado quando o producer roda com
# --destino kinesis. Vem do .env para não fixar infraestrutura no código.
import os

KINESIS_STREAM_NAME = os.getenv("KINESIS_STREAM_NAME", "fiap-alfabetizacao-stream")

# Colunas de metadados adicionadas pelo pipeline batch que não fazem
# parte do evento "cru" e são removidas antes do envio.
COLUNAS_METADADOS_BATCH = [
    "entidade_origem",
    "modo_ingestao",
    "data_ingestao_bronze",
]
