from src.bronze.processar_bronze import processar_camada_bronze
from src.silver.processar_silver import processar_camada_silver


def main() -> None:
    processar_camada_bronze()
    processar_camada_silver()


if __name__ == "__main__":
    main()
