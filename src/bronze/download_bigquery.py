"""
Download das tabelas Bronze a partir do BigQuery (Base dos Dados).

Versão em script do notebook 01_download_bronze_bigquery.ipynb,
para execução reproduzível sem Jupyter.

Autenticação (em ordem de tentativa):
1. Application Default Credentials (gcloud auth application-default login);
2. Login interativo pelo navegador via pydata-google-auth
   (não exige gcloud CLI instalado; as credenciais ficam em cache local).

Uso:
    python -m src.bronze.download_bigquery
    python -m src.bronze.download_bigquery --tabelas uf municipio
    python -m src.bronze.download_bigquery --somente-dry-run
"""

import argparse
import os
from datetime import datetime
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

SCOPES = ["https://www.googleapis.com/auth/bigquery"]

QUERIES_PATH = Path("queries/bronze")
BRONZE_BASE_PATH = Path("data/bronze")

TABELAS = [
    "uf",
    "meta_alfabetizacao_brasil",
    "meta_alfabetizacao_uf",
    "meta_alfabetizacao_municipio",
    "municipio",
    "alunos",
]


def obter_credenciais():
    """
    Obtém credenciais Google, tentando primeiro as Application Default
    Credentials e, na ausência delas, abrindo o navegador para login.
    """
    import google.auth
    from google.auth.exceptions import DefaultCredentialsError

    try:
        credenciais, _ = google.auth.default(scopes=SCOPES)
        print("Autenticado via Application Default Credentials")
        return credenciais
    except DefaultCredentialsError:
        pass

    import pydata_google_auth

    print("Abrindo navegador para login Google...")
    credenciais = pydata_google_auth.get_user_credentials(SCOPES)
    print("Autenticado via login interativo")

    return credenciais


def carregar_query(nome_tabela: str) -> str:
    caminho_query = QUERIES_PATH / f"{nome_tabela}.sql"

    with open(caminho_query, "r", encoding="utf-8") as arquivo:
        return arquivo.read()


def estimar_consultas(client, tabelas: list[str]) -> pd.DataFrame:
    """
    Executa dry run de cada consulta para estimar o volume processado,
    sem custo e sem baixar dados.
    """
    from google.cloud import bigquery

    estimativas = []

    for nome_tabela in tabelas:
        query = carregar_query(nome_tabela)

        job_config = bigquery.QueryJobConfig(dry_run=True, use_query_cache=False)
        dry_run_job = client.query(query, job_config=job_config)

        mb_estimados = dry_run_job.total_bytes_processed / 1024 / 1024

        estimativas.append(
            {
                "tabela": nome_tabela,
                "mb_estimados": round(mb_estimados, 2),
            }
        )

    return pd.DataFrame(estimativas)


def baixar_tabela(client, nome_tabela: str, max_bytes_billed: int, execution_date: str) -> dict:
    """
    Baixa uma tabela do BigQuery e salva na Bronze em formato parquet.

    Se o arquivo local já existir, a consulta não é executada novamente.
    """
    from google.cloud import bigquery

    tabela_path = BRONZE_BASE_PATH / nome_tabela / f"execution_date={execution_date}"
    output_file = tabela_path / f"{nome_tabela}.parquet"

    if output_file.exists():
        df_local = pd.read_parquet(output_file)
        print(f"[SKIP] {nome_tabela}: arquivo já existe ({len(df_local)} linhas)")

        return {"tabela": nome_tabela, "status": "ja_existia", "linhas": len(df_local)}

    print(f"[RUN] {nome_tabela}: executando consulta...")

    job_config = bigquery.QueryJobConfig(
        maximum_bytes_billed=max_bytes_billed,
        use_query_cache=True,
    )

    query_job = client.query(carregar_query(nome_tabela), job_config=job_config)
    df = query_job.to_dataframe()

    tabela_path.mkdir(parents=True, exist_ok=True)
    df.to_parquet(output_file, index=False)

    print(f"[OK] {nome_tabela}: {len(df)} linhas salvas em {output_file}")

    return {"tabela": nome_tabela, "status": "baixado", "linhas": len(df)}


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Download das tabelas Bronze a partir do BigQuery."
    )
    parser.add_argument(
        "--tabelas",
        nargs="+",
        default=TABELAS,
        choices=TABELAS,
        help="Tabelas a baixar (padrão: todas).",
    )
    parser.add_argument(
        "--somente-dry-run",
        action="store_true",
        help="Apenas estima o volume das consultas, sem baixar dados.",
    )

    argumentos = parser.parse_args()

    load_dotenv()

    project_id = os.getenv("GCP_PROJECT_ID")
    max_bytes_billed = int(os.getenv("BQ_MAX_BYTES_BILLED", "400000000"))

    if not project_id:
        raise ValueError(
            "GCP_PROJECT_ID não encontrado. "
            "Copie .env.example para .env e preencha o projeto Google Cloud."
        )

    from google.cloud import bigquery

    credenciais = obter_credenciais()
    client = bigquery.Client(project=project_id, credentials=credenciais)

    print(f"Projeto GCP: {project_id}")
    print(f"Limite por consulta: {max_bytes_billed / 1024 / 1024:.0f} MB")

    print("\nEstimativa de volume (dry run):")
    df_estimativas = estimar_consultas(client, argumentos.tabelas)
    print(df_estimativas.to_string(index=False))

    if argumentos.somente_dry_run:
        print("\nDry run concluído. Nenhum dado foi baixado.")
        return

    execution_date = datetime.now().strftime("%Y-%m-%d")

    print("\nIniciando download:")
    resultados = [
        baixar_tabela(client, tabela, max_bytes_billed, execution_date)
        for tabela in argumentos.tabelas
    ]

    print("\nResumo:")
    print(pd.DataFrame(resultados).to_string(index=False))


if __name__ == "__main__":
    main()
