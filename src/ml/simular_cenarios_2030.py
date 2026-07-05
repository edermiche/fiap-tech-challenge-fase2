"""
Simulacao de cenarios de alfabetizacao municipal ate 2030.

Esta rotina usa o resultado municipal observado mais recente e as metas oficiais
anuais para criar cenarios prospectivos. Nao e uma previsao temporal estatistica
robusta; e uma simulacao explicavel para apoiar analise de risco territorial.
"""
from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd

from src.common.particionamento import ler_tabela_mais_recente, salvar_particionado_por_ano


SILVER_PATH = Path("data/silver")
GOLD_PATH = Path("data/gold")
EXECUTION_DATE = date.today().isoformat()
ANO_FINAL = 2030

CODIGO_UF_POR_PREFIXO = {
    "11": "RO",
    "12": "AC",
    "13": "AM",
    "14": "RR",
    "15": "PA",
    "16": "AP",
    "17": "TO",
    "21": "MA",
    "22": "PI",
    "23": "CE",
    "24": "RN",
    "25": "PB",
    "26": "PE",
    "27": "AL",
    "28": "SE",
    "29": "BA",
    "31": "MG",
    "32": "ES",
    "33": "RJ",
    "35": "SP",
    "41": "PR",
    "42": "SC",
    "43": "RS",
    "50": "MS",
    "51": "MT",
    "52": "GO",
    "53": "DF",
}


def carregar_silver(nome_tabela: str, colunas: list[str] | None = None) -> pd.DataFrame:
    return ler_tabela_mais_recente(SILVER_PATH / nome_tabela, colunas=colunas)


def salvar_gold(df: pd.DataFrame, nome_tabela: str) -> Path:
    output_dir = GOLD_PATH / nome_tabela / f"execution_date={EXECUTION_DATE}"
    salvar_particionado_por_ano(df, output_dir, f"{nome_tabela}.parquet")
    return output_dir


def classificar_risco(gap: float, probabilidade: float) -> str:
    if pd.isna(gap):
        return "Sem informacao"
    if gap <= 0:
        return "Meta atingida"
    if probabilidade >= 80:
        return "Baixo risco"
    if gap <= 5:
        return "Risco moderado"
    if gap <= 15:
        return "Risco alto"
    return "Risco critico"


def calcular_probabilidade_atingir_meta(
    taxa_simulada: pd.Series,
    meta: pd.Series,
    percentual_participacao: pd.Series,
) -> pd.Series:
    folga = taxa_simulada - meta
    prob = 50 + (folga * 4)
    prob = prob + ((percentual_participacao.fillna(0) - 85) * 0.6)
    return prob.clip(lower=0, upper=100).round(2)


def preparar_base_municipal() -> pd.DataFrame:
    resultados = carregar_silver(
        "fato_resultado_meta_municipio",
        colunas=[
            "ano",
            "id_municipio",
            "rede",
            "taxa_alfabetizacao",
            "nivel_alfabetizacao",
            "percentual_participacao",
            "nivel_agregacao",
        ],
    )
    metas = carregar_silver(
        "fato_meta_anual_municipio",
        colunas=["ano", "id_municipio", "rede", "ano_meta", "meta_alfabetizacao"],
    )
    municipios = carregar_silver(
        "dim_municipio",
        colunas=["id_municipio", "id_municipio_nome"],
    )
    bolsa = carregar_silver(
        "fato_bolsa_familia_municipio",
        colunas=["ano_competencia", "id_municipio", "total_beneficiarios", "valor_total_pago"],
    )

    resultados = resultados.dropna(subset=["taxa_alfabetizacao"]).copy()
    ano_base = int(resultados["ano"].max())
    base = resultados[resultados["ano"] == ano_base].copy()

    base["id_municipio"] = base["id_municipio"].astype(str)
    municipios["id_municipio"] = municipios["id_municipio"].astype(str)
    base = base.merge(
        municipios.drop_duplicates("id_municipio"),
        on="id_municipio",
        how="left",
    )

    bolsa = bolsa.copy()
    bolsa["id_municipio"] = bolsa["id_municipio"].astype(str)
    bolsa = bolsa[bolsa["ano_competencia"] == ano_base]
    bolsa = bolsa.rename(
        columns={
            "total_beneficiarios": "total_beneficiarios_bolsa_familia",
            "valor_total_pago": "valor_total_bolsa_familia",
        }
    )
    base = base.merge(
        bolsa[
            [
                "id_municipio",
                "total_beneficiarios_bolsa_familia",
                "valor_total_bolsa_familia",
            ]
        ].drop_duplicates("id_municipio"),
        on="id_municipio",
        how="left",
    )

    metas = metas.copy()
    metas["id_municipio"] = metas["id_municipio"].astype(str)
    metas = metas[(metas["ano"] == ano_base) & (metas["ano_meta"] >= ano_base)]

    df = base.merge(
        metas,
        on=["ano", "id_municipio", "rede"],
        how="inner",
    )
    df["sigla_uf"] = df["id_municipio"].str[:2].map(CODIGO_UF_POR_PREFIXO)
    return df


def simular_cenarios_2030() -> pd.DataFrame:
    df = preparar_base_municipal()
    ano_base = int(df["ano"].max())
    anos_restantes = (ANO_FINAL - ano_base) + 1
    progresso = (df["ano_meta"] - ano_base + 1) / anos_restantes

    taxa_atual = pd.to_numeric(df["taxa_alfabetizacao"], errors="coerce")
    meta_2030 = (
        df[df["ano_meta"] == ANO_FINAL][["id_municipio", "rede", "meta_alfabetizacao"]]
        .rename(columns={"meta_alfabetizacao": "meta_2030"})
        .drop_duplicates(["id_municipio", "rede"])
    )
    df = df.merge(meta_2030, on=["id_municipio", "rede"], how="left")
    meta_2030_col = pd.to_numeric(df["meta_2030"], errors="coerce")
    gap_total = (meta_2030_col - taxa_atual).clip(lower=0)

    participacao = pd.to_numeric(df["percentual_participacao"], errors="coerce").fillna(85)
    fator_base = (0.72 + ((participacao - 80) / 100)).clip(lower=0.65, upper=0.9)

    df["taxa_atual"] = taxa_atual.round(2)
    df["taxa_simulada_conservador"] = (taxa_atual + gap_total * 0.45 * progresso).clip(upper=100).round(2)
    df["taxa_simulada_base"] = (taxa_atual + gap_total * fator_base * progresso).clip(upper=100).round(2)
    df["taxa_simulada_acelerado"] = (taxa_atual + gap_total * 1.18 * progresso).clip(upper=100).round(2)

    df["gap_conservador"] = (df["meta_alfabetizacao"] - df["taxa_simulada_conservador"]).round(2)
    df["gap_base"] = (df["meta_alfabetizacao"] - df["taxa_simulada_base"]).round(2)
    df["gap_acelerado"] = (df["meta_alfabetizacao"] - df["taxa_simulada_acelerado"]).round(2)

    df["probabilidade_atingir_meta_base"] = calcular_probabilidade_atingir_meta(
        df["taxa_simulada_base"],
        df["meta_alfabetizacao"],
        df["percentual_participacao"],
    )
    df["classe_risco_2030"] = [
        classificar_risco(gap, prob)
        for gap, prob in zip(df["gap_base"], df["probabilidade_atingir_meta_base"])
    ]
    df["status_cenario_base"] = "Abaixo da meta"
    df.loc[df["gap_base"] <= 0, "status_cenario_base"] = "Meta atingida"
    df["data_processamento_gold"] = EXECUTION_DATE

    colunas = [
        "ano",
        "ano_meta",
        "id_municipio",
        "id_municipio_nome",
        "sigla_uf",
        "rede",
        "nivel_agregacao",
        "nivel_alfabetizacao",
        "percentual_participacao",
        "total_beneficiarios_bolsa_familia",
        "valor_total_bolsa_familia",
        "taxa_atual",
        "meta_alfabetizacao",
        "meta_2030",
        "taxa_simulada_conservador",
        "taxa_simulada_base",
        "taxa_simulada_acelerado",
        "gap_conservador",
        "gap_base",
        "gap_acelerado",
        "probabilidade_atingir_meta_base",
        "status_cenario_base",
        "classe_risco_2030",
        "data_processamento_gold",
    ]

    return (
        df[colunas]
        .rename(columns={"ano": "ano_base", "ano_meta": "ano"})
        .sort_values(["ano", "sigla_uf", "id_municipio", "rede"])
        .reset_index(drop=True)
    )


def processar_simulacao_2030() -> Path:
    print("Gerando simulacao de cenarios ate 2030")
    df = simular_cenarios_2030()
    output_dir = salvar_gold(df, "simulacao_alfabetizacao_2030")
    print(f"[OK] gold.simulacao_alfabetizacao_2030 salva: {len(df)} linhas em {output_dir}")
    return output_dir


if __name__ == "__main__":
    processar_simulacao_2030()
