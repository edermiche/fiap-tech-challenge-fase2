"""
Carregador específico para o arquivo FUNDEB de downloads.
"""
from datetime import datetime
from pathlib import Path

import pandas as pd

from src.bronze.config import BRONZE_PATH


def carregar_fundeb_de_downloads() -> None:
    """
    Lê o arquivo FUNDEB de downloads/ e salva na estrutura bronze.
    """
    arquivo_downloads = Path("downloads/fundeb_2024_2025_por_estado.csv")
    
    if not arquivo_downloads.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {arquivo_downloads}")
    
    print(f"Lendo FUNDEB de: {arquivo_downloads}")
    
    # Ler CSV
    df = pd.read_csv(arquivo_downloads, encoding="utf-8")
    
    # Salvar em Bronze
    execution_date = datetime.now().strftime("%Y-%m-%d")
    fundeb_path = BRONZE_PATH / "fundeb" / f"execution_date={execution_date}"
    fundeb_path.mkdir(parents=True, exist_ok=True)
    
    output_file = fundeb_path / "fundeb.parquet"
    df.to_parquet(output_file, index=False)
    
    print(f"[OK] FUNDEB salvo em: {output_file}")
    print(f"     linhas: {len(df)} | colunas: {len(df.columns)}")
