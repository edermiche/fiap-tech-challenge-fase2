from datetime import date

from src.bronze.processar_bronze import processar_camada_bronze
from src.silver.processar_silver import processar_camada_silver
from src.gold.processar_gold import processar_camada_gold


def main() -> None:
    """Executa o fluxo completo: Bronze -> Silver -> Gold."""
    # A data é resolvida uma vez e repassada às camadas: Silver e Gold
    # precisam gravar na mesma partição execution_date.
    data_processamento = date.today()

    processar_camada_bronze()
    processar_camada_silver(data_processamento)
    processar_camada_gold(data_processamento)


if __name__ == "__main__":
    main()
