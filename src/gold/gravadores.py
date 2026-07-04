import shutil
from pathlib import Path

import pandas as pd

from src.gold.config import GOLD_PATH


def salvar_gold(df: pd.DataFrame, nome_tabela: str) -> Path:
    """
    Salva uma tabela analítica da camada Gold em Parquet, particionada
    por ano (estilo Hive), quando a coluna `ano` existe:

        data/gold/{nome_tabela}/ano=YYYY/{nome_tabela}.parquet

    O particionamento por ano habilita partition pruning nas consultas
    (FinOps). Tabelas sem `ano` são gravadas como arquivo único.
    A gravação é idempotente (a pasta é recriada a cada execução).
    """
    output_base = GOLD_PATH / nome_tabela

    if output_base.exists():
        shutil.rmtree(output_base)

    output_base.mkdir(parents=True, exist_ok=True)

    if "ano" in df.columns:
        anos = sorted(a for a in df["ano"].dropna().unique())

        for ano in anos:
            particao = df[df["ano"] == ano].drop(columns=["ano"])
            pasta = output_base / f"ano={int(ano)}"
            pasta.mkdir(parents=True, exist_ok=True)
            particao.to_parquet(pasta / f"{nome_tabela}.parquet", index=False)

        nulos = df[df["ano"].isna()]
        if len(nulos) > 0:
            pasta = output_base / "ano=__null__"
            pasta.mkdir(parents=True, exist_ok=True)
            nulos.drop(columns=["ano"]).to_parquet(
                pasta / f"{nome_tabela}.parquet", index=False
            )

        print(f"[OK] gold.{nome_tabela} salva particionada por ano em: {output_base}")
        print(f"     Partições (ano): {[int(a) for a in anos]}")
    else:
        arquivo = output_base / f"{nome_tabela}.parquet"
        df.to_parquet(arquivo, index=False)
        print(f"[OK] gold.{nome_tabela} salva (sem partição) em: {arquivo}")

    print(f"     Linhas: {len(df)} | Colunas: {len(df.columns)}")

    return output_base
