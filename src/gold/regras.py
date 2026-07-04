import pandas as pd


def aplicar_status_meta(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula a distância em relação à meta e classifica o status.

    Regras:
    - distancia_meta = taxa_alfabetizacao - meta_alfabetizacao;
    - flag_meta_atingida = True quando a distância é >= 0, False quando
      é negativa, e <NA> quando taxa ou meta estão ausentes;
    - status_meta: "Meta atingida", "Abaixo da meta" ou "Sem informação".

    Observação técnica:
    a flag é construída como coluna de tipo object (True/False/pd.NA)
    para evitar erro de coerção do pandas 2.2+ ao inserir valores nulos
    em uma coluna booleana.
    """
    df = df.copy()

    df["distancia_meta"] = df["taxa_alfabetizacao"] - df["meta_alfabetizacao"]

    mask_sem_info = (
        df["taxa_alfabetizacao"].isna() | df["meta_alfabetizacao"].isna()
    )
    mask_atingida = (df["distancia_meta"] >= 0) & ~mask_sem_info
    mask_abaixo = (df["distancia_meta"] < 0) & ~mask_sem_info

    flag = pd.Series(pd.NA, index=df.index, dtype="object")
    flag[mask_atingida] = True
    flag[mask_abaixo] = False
    df["flag_meta_atingida"] = flag

    df["status_meta"] = "Sem informação"
    df.loc[mask_atingida, "status_meta"] = "Meta atingida"
    df.loc[mask_abaixo, "status_meta"] = "Abaixo da meta"

    return df
