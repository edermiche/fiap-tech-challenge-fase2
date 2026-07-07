from dataclasses import dataclass, field
import re
import unicodedata

import pandas as pd


@dataclass(frozen=True)
class RegraQualidade:
    chave_primaria: list[str]
    campos_obrigatorios: list[str] = field(default_factory=list)
    tipos: dict[str, str] = field(default_factory=dict)


TIPOS_BASE = {
    "ano": "Int64",
    "ano_competencia": "Int64",
    "ano_meta": "Int64",
    "nivel_alfabetizacao": "Int64",
    "ranking_ano": "Int64",
    "id_aluno": "string",
    "id_escola": "string",
    "id_municipio": "string",
    "sigla_uf": "string",
    "rede": "string",
    "serie": "string",
    "modo_ingestao": "string",
    "data_processamento_silver": "string",
}


TIPOS_NUMERICOS = {
    "taxa_alfabetizacao": "Float64",
    "media_portugues": "Float64",
    "meta_alfabetizacao": "Float64",
    "percentual_participacao": "Float64",
    "proporcao_alunos": "Float64",
    "proficiencia": "Float64",
    "peso_aluno": "Float64",
    "total_beneficiarios": "Int64",
    "valor_total_pago": "Float64",
    "total_estado_df": "Float64",
    "total_municipios": "Float64",
    "total_fundeb": "Float64",
    "percentual_brasil": "Float64",
}


REGRAS_QUALIDADE = {
    "dominio_regiao_uf": RegraQualidade(
        chave_primaria=["sigla_uf"],
        campos_obrigatorios=["sigla_uf", "regiao_brasil"],
    ),
    "dim_uf": RegraQualidade(
        chave_primaria=["sigla_uf"],
        campos_obrigatorios=["sigla_uf", "sigla_uf_nome", "regiao_brasil"],
    ),
    "dim_municipio": RegraQualidade(
        chave_primaria=["id_municipio"],
        campos_obrigatorios=["id_municipio", "id_municipio_nome"],
    ),
    "dim_escola": RegraQualidade(
        chave_primaria=["id_escola"],
        campos_obrigatorios=["id_escola", "id_municipio"],
    ),
    "fato_resultado_brasil": RegraQualidade(
        chave_primaria=["ano", "rede", "nivel_agregacao"],
        campos_obrigatorios=["ano", "rede", "taxa_alfabetizacao", "nivel_agregacao"],
    ),
    "fato_resultado_uf": RegraQualidade(
        chave_primaria=["ano", "sigla_uf", "serie", "rede"],
        campos_obrigatorios=["ano", "sigla_uf", "serie", "rede", "taxa_alfabetizacao"],
    ),
    "fato_resultado_municipio": RegraQualidade(
        chave_primaria=["ano", "id_municipio", "serie", "rede"],
        campos_obrigatorios=["ano", "id_municipio", "serie", "rede", "taxa_alfabetizacao"],
    ),
    "fato_resultado_meta_uf": RegraQualidade(
        chave_primaria=["ano", "sigla_uf", "rede", "nivel_agregacao"],
        campos_obrigatorios=["ano", "sigla_uf", "rede", "taxa_alfabetizacao"],
    ),
    "fato_resultado_meta_municipio": RegraQualidade(
        chave_primaria=["ano", "id_municipio", "rede", "nivel_alfabetizacao"],
        campos_obrigatorios=[
            "ano",
            "id_municipio",
            "rede",
            "nivel_alfabetizacao",
            "taxa_alfabetizacao",
        ],
    ),
    "fato_meta_anual_brasil": RegraQualidade(
        chave_primaria=["ano", "rede", "ano_meta", "nivel_agregacao"],
        campos_obrigatorios=["ano", "rede", "ano_meta", "meta_alfabetizacao"],
    ),
    "fato_meta_anual_uf": RegraQualidade(
        chave_primaria=["ano", "sigla_uf", "rede", "ano_meta"],
        campos_obrigatorios=["ano", "sigla_uf", "rede", "ano_meta", "meta_alfabetizacao"],
    ),
    "fato_meta_anual_municipio": RegraQualidade(
        chave_primaria=["ano", "id_municipio", "rede", "ano_meta"],
        campos_obrigatorios=["ano", "id_municipio", "rede", "ano_meta", "meta_alfabetizacao"],
    ),
    "fato_distribuicao_nivel_uf": RegraQualidade(
        chave_primaria=["ano", "sigla_uf", "serie", "rede", "nivel_alfabetizacao"],
        campos_obrigatorios=[
            "ano",
            "sigla_uf",
            "serie",
            "rede",
            "nivel_alfabetizacao",
            "proporcao_alunos",
        ],
    ),
    "fato_distribuicao_nivel_municipio": RegraQualidade(
        chave_primaria=["ano", "id_municipio", "serie", "rede", "nivel_alfabetizacao"],
        campos_obrigatorios=[
            "ano",
            "id_municipio",
            "serie",
            "rede",
            "nivel_alfabetizacao",
            "proporcao_alunos",
        ],
    ),
    "fato_aluno_alfabetizacao": RegraQualidade(
        chave_primaria=["ano", "id_aluno", "id_escola"],
        campos_obrigatorios=["ano", "id_aluno", "id_escola", "id_municipio"],
    ),
    "fato_bolsa_familia_municipio": RegraQualidade(
        chave_primaria=["ano_competencia", "id_municipio"],
        campos_obrigatorios=[
            "ano_competencia",
            "id_municipio",
            "sigla_uf",
            "total_beneficiarios",
            "valor_total_pago",
        ],
    ),
    "fato_fundeb": RegraQualidade(
        chave_primaria=["ano", "sigla_uf"],
        campos_obrigatorios=["ano", "sigla_uf", "total_fundeb"],
    ),
}


def normalizar_nome_coluna(nome_coluna: str) -> str:
    nome_normalizado = unicodedata.normalize("NFKD", str(nome_coluna))
    nome_normalizado = nome_normalizado.encode("ascii", "ignore").decode("ascii")
    nome_normalizado = nome_normalizado.strip().lower()
    nome_normalizado = re.sub(r"[^a-z0-9]+", "_", nome_normalizado)
    nome_normalizado = re.sub(r"_+", "_", nome_normalizado).strip("_")

    return nome_normalizado


def padronizar_nomes_colunas(df: pd.DataFrame) -> pd.DataFrame:
    nomes_usados = {}
    novos_nomes = []

    for coluna in df.columns:
        nome_base = normalizar_nome_coluna(coluna)
        nome_final = nome_base

        if nome_final in nomes_usados:
            nomes_usados[nome_base] += 1
            nome_final = f"{nome_base}_{nomes_usados[nome_base]}"
        else:
            nomes_usados[nome_base] = 0

        novos_nomes.append(nome_final)

    df_padronizado = df.copy()
    df_padronizado.columns = novos_nomes

    return df_padronizado


def aplicar_tipagem(df: pd.DataFrame, tipos: dict[str, str]) -> pd.DataFrame:
    df_tipado = df.copy()

    for coluna, tipo in tipos.items():
        if coluna not in df_tipado.columns:
            continue

        if tipo in {"Int64", "Float64"}:
            df_tipado[coluna] = pd.to_numeric(df_tipado[coluna], errors="coerce").astype(tipo)
            continue

        df_tipado[coluna] = df_tipado[coluna].astype(tipo)

    for coluna in df_tipado.columns:
        if coluna.startswith("flag_"):
            df_tipado[coluna] = df_tipado[coluna].astype("boolean")

    return df_tipado


def remover_nulos_criticos(df: pd.DataFrame, campos: list[str]) -> pd.DataFrame:
    campos_existentes = [coluna for coluna in campos if coluna in df.columns]
    if not campos_existentes:
        return df

    df_filtrado = df.dropna(subset=campos_existentes)

    for coluna in campos_existentes:
        if pd.api.types.is_string_dtype(df_filtrado[coluna]) or df_filtrado[coluna].dtype == object:
            df_filtrado = df_filtrado[df_filtrado[coluna].astype(str).str.strip() != ""]

    return df_filtrado


def aplicar_qualidade_tabela(nome_tabela: str, df: pd.DataFrame) -> pd.DataFrame:
    df = padronizar_nomes_colunas(df)
    regra = REGRAS_QUALIDADE.get(nome_tabela)
    if regra is None:
        return df.drop_duplicates().reset_index(drop=True)

    tipos = {
        **TIPOS_BASE,
        **TIPOS_NUMERICOS,
        **regra.tipos,
    }

    total_inicial = len(df)
    df_qualificado = aplicar_tipagem(df, tipos)
    df_qualificado = remover_nulos_criticos(
        df_qualificado,
        [*regra.chave_primaria, *regra.campos_obrigatorios],
    )

    chave_existente = [
        coluna
        for coluna in regra.chave_primaria
        if coluna in df_qualificado.columns
    ]
    if chave_existente:
        df_qualificado = df_qualificado.drop_duplicates(subset=chave_existente)
    else:
        df_qualificado = df_qualificado.drop_duplicates()

    df_qualificado = df_qualificado.reset_index(drop=True)
    removidos = total_inicial - len(df_qualificado)
    print(
        f"[QUALIDADE] silver.{nome_tabela}: "
        f"{total_inicial} -> {len(df_qualificado)} linhas "
        f"({removidos} removidas)"
    )

    return df_qualificado


def aplicar_qualidade_silver(
    tabelas_silver: dict[str, pd.DataFrame],
) -> dict[str, pd.DataFrame]:
    return {
        nome_tabela: aplicar_qualidade_tabela(nome_tabela, df)
        for nome_tabela, df in tabelas_silver.items()
    }
