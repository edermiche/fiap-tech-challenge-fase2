from src.bronze.processar_bronze import processar_camada_bronze
from src.silver.processar_silver import processar_camada_silver
from src.gold.processar_gold import processar_camada_gold


def main() -> None:
    processar_camada_bronze()
    processar_camada_silver()
    processar_camada_gold()



if __name__ == "__main__":
    main()
