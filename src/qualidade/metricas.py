"""
Coleta e avaliação das métricas de qualidade de cada execução.

Produz um DataFrame no formato da tabela `gold.metricas_qualidade`
(uma linha por execução/camada/tabela/regra) e aplica os limites do
catálogo de regras: acima do limite bloqueante, `avaliar_gates` levanta
`QualidadeInsuficienteError` e a execução para antes de publicar a
camada — o que impede a Gold de ser construída sobre dados corrompidos.

Ver src/qualidade/regras.py para os limites e docs/adr/ADR-002 para a
decisão de barrar em vez de apenas sinalizar.
"""
# As anotações `X | None` precisam ser adiadas: o Glue Python Shell roda 3.9.
from __future__ import annotations

import pandas as pd

from src.qualidade.regras import (
    MODO_BLOQUEAR,
    REGRAS,
    SEVERIDADE_BLOQUEANTE,
    STATUS_ALERTA,
    STATUS_BLOQUEIO,
    STATUS_OK,
    Regra,
    modo_execucao,
)
from src.silver.config import COLUNAS_NUMERICAS_META, COLUNAS_NUMERICAS_RESULTADO
from src.silver.qualidade import REGRAS_QUALIDADE


CAMADA_SILVER = "silver"
CAMADA_GOLD = "gold"

COLUNAS_METRICAS = [
    "data_execucao",
    "camada",
    "tabela",
    "regra",
    "coluna",
    "escopo",
    "registros_avaliados",
    "registros_violando",
    "percentual_violacao",
    "limite_bloqueio",
    "severidade",
    "status",
]

SUFIXOS_FLAG = ["_valido", "_valida", "_preenchido", "_preenchida"]

# Colunas cujo domínio válido é o intervalo percentual [0,100]: a flag
# correspondente é classificada na regra percentual_fora_intervalo.
COLUNAS_PERCENTUAIS = set(COLUNAS_NUMERICAS_RESULTADO) | set(COLUNAS_NUMERICAS_META)

FLAG_AUSENCIA_FONTE = "flag_dado_ausente_fonte"


class QualidadeInsuficienteError(RuntimeError):
    """Levantada quando uma regra bloqueante é violada acima do limite."""


def montar_dataframe(metricas: list[dict]) -> pd.DataFrame:
    """
    Materializa as métricas com tipos fixos.

    O schema precisa ser estável entre execuções: gold.metricas_qualidade
    é lida como série histórica, e `limite_bloqueio` é nulo nas regras de
    alerta — sem a tipagem explícita, uma execução só de alertas gravaria
    a coluna como objeto e quebraria a leitura do histórico.
    """
    return pd.DataFrame(metricas, columns=COLUNAS_METRICAS).astype(
        {
            "registros_avaliados": "int64",
            "registros_violando": "int64",
            "percentual_violacao": "float64",
            "limite_bloqueio": "float64",
        }
    )


def coluna_base_da_flag(nome_flag: str) -> str:
    nome = nome_flag[len("flag_"):]

    for sufixo in SUFIXOS_FLAG:
        if nome.endswith(sufixo):
            return nome[: -len(sufixo)]

    return nome


def regra_da_flag(nome_flag: str) -> str:
    coluna = coluna_base_da_flag(nome_flag)
    eh_percentual = coluna in COLUNAS_PERCENTUAIS or coluna.startswith(
        ("taxa_", "proporcao_", "percentual_", "meta_alfabetizacao")
    )

    return "percentual_fora_intervalo" if eh_percentual else "campo_invalido"


def classificar_status(regra: Regra, percentual: float) -> str:
    if regra.limite_bloqueio is not None and percentual > regra.limite_bloqueio:
        return STATUS_BLOQUEIO

    if regra.limite_alerta is not None and percentual > regra.limite_alerta:
        return STATUS_ALERTA

    return STATUS_OK


def montar_metrica(
    data_execucao: str,
    camada: str,
    tabela: str,
    nome_regra: str,
    avaliados: int,
    violando: int,
    coluna: str = "",
    escopo: str = "",
    percentual: float | None = None,
) -> dict:
    regra = REGRAS[nome_regra]

    if percentual is None:
        percentual = 100.0 * violando / avaliados if avaliados else 0.0

    return {
        "data_execucao": data_execucao,
        "camada": camada,
        "tabela": tabela,
        "regra": nome_regra,
        "coluna": coluna,
        "escopo": escopo,
        "registros_avaliados": int(avaliados),
        "registros_violando": int(violando),
        "percentual_violacao": round(float(percentual), 4),
        "limite_bloqueio": regra.limite_bloqueio,
        "severidade": regra.severidade,
        "status": classificar_status(regra, percentual),
    }


def _metricas_de_flags(
    data_execucao: str,
    nome_tabela: str,
    df: pd.DataFrame,
) -> list[dict]:
    metricas = []

    for coluna in df.columns:
        if not coluna.startswith("flag_") or coluna == FLAG_AUSENCIA_FONTE:
            continue

        reprovados = int((~df[coluna].fillna(True).astype(bool)).sum())
        metricas.append(
            montar_metrica(
                data_execucao,
                CAMADA_SILVER,
                nome_tabela,
                regra_da_flag(coluna),
                avaliados=len(df),
                violando=reprovados,
                coluna=coluna_base_da_flag(coluna),
            )
        )

    return metricas


def _metricas_estruturais(
    data_execucao: str,
    nome_tabela: str,
    df: pd.DataFrame,
) -> list[dict]:
    metricas = [
        montar_metrica(
            data_execucao,
            CAMADA_SILVER,
            nome_tabela,
            "tabela_vazia",
            avaliados=max(len(df), 1),
            violando=0 if len(df) else 1,
            percentual=0.0 if len(df) else 100.0,
        )
    ]

    regra_tabela = REGRAS_QUALIDADE.get(nome_tabela)
    if regra_tabela is None:
        return metricas

    chave = [coluna for coluna in regra_tabela.chave_primaria if coluna in df.columns]
    if chave:
        metricas.append(
            montar_metrica(
                data_execucao,
                CAMADA_SILVER,
                nome_tabela,
                "chave_primaria_duplicada",
                avaliados=len(df),
                violando=int(df.duplicated(subset=chave).sum()),
                coluna="+".join(chave),
            )
        )

    for coluna in regra_tabela.campos_obrigatorios:
        if coluna not in df.columns:
            continue

        metricas.append(
            montar_metrica(
                data_execucao,
                CAMADA_SILVER,
                nome_tabela,
                "nulo_em_campo_obrigatorio",
                avaliados=len(df),
                violando=int(df[coluna].isna().sum()),
                coluna=coluna,
            )
        )

    return metricas


def coletar_metricas_silver(
    tabelas_silver: dict[str, pd.DataFrame],
    volumetria_limpeza: dict[str, tuple[int, int, int]],
    data_execucao: str,
) -> pd.DataFrame:
    """
    Monta as métricas de qualidade da camada Silver.

    volumetria_limpeza traz (linhas_iniciais, linhas_apos_descarte,
    linhas_finais) por tabela, devolvido por
    src.silver.qualidade.aplicar_qualidade_silver — o que separa perda de
    dado (chave inválida) de deduplicação esperada.
    """
    metricas: list[dict] = []

    for nome_tabela, df in tabelas_silver.items():
        metricas.extend(_metricas_estruturais(data_execucao, nome_tabela, df))
        metricas.extend(_metricas_de_flags(data_execucao, nome_tabela, df))

        iniciais, apos_descarte, finais = volumetria_limpeza.get(
            nome_tabela, (len(df), len(df), len(df))
        )
        metricas.append(
            montar_metrica(
                data_execucao,
                CAMADA_SILVER,
                nome_tabela,
                "chave_invalida_descartada",
                avaliados=iniciais,
                violando=max(iniciais - apos_descarte, 0),
            )
        )
        metricas.append(
            montar_metrica(
                data_execucao,
                CAMADA_SILVER,
                nome_tabela,
                "duplicidade_removida",
                avaliados=apos_descarte,
                violando=max(apos_descarte - finais, 0),
            )
        )

        if FLAG_AUSENCIA_FONTE in df.columns:
            metricas.append(
                montar_metrica(
                    data_execucao,
                    CAMADA_SILVER,
                    nome_tabela,
                    "metrica_ausente_fonte",
                    avaliados=len(df),
                    violando=int(df[FLAG_AUSENCIA_FONTE].fillna(False).astype(bool).sum()),
                )
            )

    return montar_dataframe(metricas)


def coletar_metricas_gold(
    volumetria_gold: dict[str, int],
    data_execucao: str,
) -> pd.DataFrame:
    """Monta as métricas da camada Gold (volumetria publicada por tabela)."""
    metricas = [
        montar_metrica(
            data_execucao,
            CAMADA_GOLD,
            nome_tabela,
            "tabela_gold_vazia",
            avaliados=max(linhas, 1),
            violando=0 if linhas else 1,
            percentual=0.0 if linhas else 100.0,
        )
        for nome_tabela, linhas in sorted(volumetria_gold.items())
    ]

    return montar_dataframe(metricas)


def coletar_metricas_cobertura(
    coberturas: dict[str, dict[int, tuple[int, int]]],
    data_execucao: str,
) -> pd.DataFrame:
    """
    Monta as métricas de cobertura territorial das tabelas Gold.

    `coberturas` mapeia tabela -> ano -> (entidades presentes, esperadas).
    Uma UF que some do recorte de um ano — porque a fonte não publicou a
    meta daquele ano, por exemplo — desaparece hoje em silêncio; aqui a
    lacuna vira uma linha do histórico, comparável entre execuções.
    """
    metricas = [
        montar_metrica(
            data_execucao,
            CAMADA_GOLD,
            nome_tabela,
            "cobertura_territorial",
            avaliados=esperadas,
            violando=max(esperadas - presentes, 0),
            escopo=f"ano={ano}",
        )
        for nome_tabela, por_ano in sorted(coberturas.items())
        for ano, (presentes, esperadas) in sorted(por_ano.items())
    ]

    return montar_dataframe(metricas)


def comparar_cobertura_com_safra_anterior(
    df_metricas: pd.DataFrame,
    df_anterior: pd.DataFrame | None,
) -> pd.DataFrame:
    """
    Acrescenta a métrica de queda de cobertura contra a execução anterior.

    Enquanto `cobertura_territorial` mede a lacuna contra o universo
    esperado (e tolera a ausência estrutural conhecida da fonte), esta
    regra compara com a própria safra anterior: qualquer entidade que
    existia e sumiu vira alerta, porque cobertura não deve regredir.
    """
    if df_anterior is None or df_anterior.empty or df_metricas.empty:
        return df_metricas

    atual = df_metricas[df_metricas["regra"] == "cobertura_territorial"]
    anterior = df_anterior[df_anterior.get("regra") == "cobertura_territorial"]

    if atual.empty or anterior.empty:
        return df_metricas

    presentes_antes = {
        (linha["tabela"], linha["escopo"]):
            int(linha["registros_avaliados"]) - int(linha["registros_violando"])
        for _, linha in anterior.iterrows()
    }
    data_execucao = str(df_metricas["data_execucao"].iloc[0])

    comparativos = []
    for _, linha in atual.iterrows():
        chave = (linha["tabela"], linha["escopo"])
        if chave not in presentes_antes:
            continue

        antes = presentes_antes[chave]
        agora = int(linha["registros_avaliados"]) - int(linha["registros_violando"])
        comparativos.append(
            montar_metrica(
                data_execucao,
                CAMADA_GOLD,
                str(linha["tabela"]),
                "queda_cobertura_safra_anterior",
                avaliados=antes,
                violando=max(antes - agora, 0),
                escopo=str(linha["escopo"]),
            )
        )

    if not comparativos:
        return df_metricas

    return pd.concat(
        [df_metricas, montar_dataframe(comparativos)],
        ignore_index=True,
    )


def comparar_com_safra_anterior(
    df_metricas: pd.DataFrame,
    df_anterior: pd.DataFrame | None,
) -> pd.DataFrame:
    """
    Acrescenta a métrica comparativa entre a execução atual e a anterior.

    É a pergunta que qualidade de dados existe para responder — "a
    ausência de métrica aumentou desde a safra anterior?" — e só tem
    resposta porque o histórico fica gravado em gold.metricas_qualidade.
    """
    if df_anterior is None or df_anterior.empty or df_metricas.empty:
        return df_metricas

    atual = df_metricas[df_metricas["regra"] == "metrica_ausente_fonte"]
    anterior = df_anterior[df_anterior["regra"] == "metrica_ausente_fonte"]

    if atual.empty or anterior.empty:
        return df_metricas

    percentual_anterior = dict(zip(anterior["tabela"], anterior["percentual_violacao"]))
    data_execucao = str(df_metricas["data_execucao"].iloc[0])

    comparativos = []
    for _, linha in atual.iterrows():
        if linha["tabela"] not in percentual_anterior:
            continue

        variacao = float(linha["percentual_violacao"]) - float(
            percentual_anterior[linha["tabela"]]
        )
        comparativos.append(
            montar_metrica(
                data_execucao,
                CAMADA_SILVER,
                str(linha["tabela"]),
                "aumento_ausencia_safra_anterior",
                avaliados=int(linha["registros_avaliados"]),
                violando=int(linha["registros_violando"]),
                coluna=FLAG_AUSENCIA_FONTE,
                percentual=max(variacao, 0.0),
            )
        )

    if not comparativos:
        return df_metricas

    return pd.concat(
        [df_metricas, montar_dataframe(comparativos)],
        ignore_index=True,
    )


def violacoes_bloqueantes(df_metricas: pd.DataFrame) -> pd.DataFrame:
    if df_metricas.empty:
        return df_metricas

    return df_metricas[
        (df_metricas["severidade"] == SEVERIDADE_BLOQUEANTE)
        & (df_metricas["status"] == STATUS_BLOQUEIO)
    ]


def imprimir_resumo(df_metricas: pd.DataFrame) -> None:
    if df_metricas.empty:
        print("[QUALIDADE] nenhuma métrica coletada")
        return

    contagem = df_metricas["status"].value_counts().to_dict()
    print(
        f"[QUALIDADE] {len(df_metricas)} métricas coletadas | "
        f"ok={contagem.get(STATUS_OK, 0)} "
        f"alerta={contagem.get(STATUS_ALERTA, 0)} "
        f"bloqueio={contagem.get(STATUS_BLOQUEIO, 0)}"
    )

    alertas = df_metricas[df_metricas["status"] == STATUS_ALERTA]
    for _, linha in alertas.iterrows():
        print(
            f"[QUALIDADE][ALERTA] {linha['camada']}.{linha['tabela']} "
            f"{linha['regra']}({linha['coluna'] or linha['escopo']}): "
            f"{linha['percentual_violacao']:.2f}% "
            f"({linha['registros_violando']}/{linha['registros_avaliados']})"
        )


def avaliar_gates(df_metricas: pd.DataFrame) -> pd.DataFrame:
    """
    Aplica o gate de qualidade. Levanta QualidadeInsuficienteError quando
    há violação bloqueante e o modo é `bloquear` (padrão).
    """
    violacoes = violacoes_bloqueantes(df_metricas)

    if violacoes.empty:
        print("[QUALIDADE] gate aprovado: nenhuma regra bloqueante violada")
        return violacoes

    detalhes = "\n".join(
        f"  - {linha['camada']}.{linha['tabela']} "
        f"{linha['regra']}({linha['coluna'] or linha['escopo']}): "
        f"{linha['percentual_violacao']:.2f}% "
        f"({linha['registros_violando']}/{linha['registros_avaliados']} registros) "
        f"> limite {linha['limite_bloqueio']:.2f}%"
        for _, linha in violacoes.iterrows()
    )

    if modo_execucao() != MODO_BLOQUEAR:
        print(
            "[QUALIDADE][ALERTA] QUALIDADE_MODO=alertar — violações bloqueantes "
            f"registradas e ignoradas:\n{detalhes}"
        )
        return violacoes

    raise QualidadeInsuficienteError(
        f"Gate de qualidade reprovado ({len(violacoes)} violações bloqueantes). "
        "A camada não foi publicada e o pipeline foi interrompido.\n"
        f"{detalhes}\n"
        "Métricas gravadas em gold.metricas_qualidade para auditoria. "
        "Para investigar sem interromper, rode com QUALIDADE_MODO=alertar."
    )
