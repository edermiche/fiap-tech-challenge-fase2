from datetime import date
from pathlib import Path


# ------------------------------------------------------------
# Caminhos das camadas
# ------------------------------------------------------------
# A Gold consome exclusivamente a Silver e escreve na Gold.
# Não há leitura da Bronze nesta camada (princípio medalhão).
# ------------------------------------------------------------

SILVER_PATH = Path("data/silver")
GOLD_PATH = Path("data/gold")

EXECUTION_DATE = date.today().isoformat()
