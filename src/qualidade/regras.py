"""
Catálogo de regras de qualidade do pipeline: o que é medido, com que
severidade e a partir de que percentual de violação a execução é barrada.

Duas decisões de projeto convivem aqui:

1. Ausência de métrica vinda da fonte (INEP/Saeb) continua sendo
   sinalizada, nunca descartada — é informação legítima sobre a origem
   (ver src/silver/transformacoes.sinalizar_dado_ausente_fonte).
2. Violação de regra estrutural (chave duplicada, tabela vazia, campo
   obrigatório nulo, percentual fora de [0,100]) **barra a execução**
   acima do limite tolerado: sinalizar sem interromper deixaria a Gold
   ser construída sobre uma extração corrompida, e o dashboard exibiria
   número errado com aparência de normalidade.

O modo é controlável por variável de ambiente `QUALIDADE_MODO`:

- `bloquear` (padrão): violação de regra bloqueante interrompe o pipeline
  antes de publicar a Silver — na AWS, o job Glue falha e dispara o
  alerta SNS já existente.
- `alertar`: registra e segue em frente. Usar apenas em exploração local.
"""
# As anotações `X | None` precisam ser adiadas: o Glue Python Shell roda 3.9.
from __future__ import annotations

import os
from dataclasses import dataclass


SEVERIDADE_BLOQUEANTE = "bloqueante"
SEVERIDADE_ALERTA = "alerta"

STATUS_OK = "ok"
STATUS_ALERTA = "alerta"
STATUS_BLOQUEIO = "bloqueio"

MODO_BLOQUEAR = "bloquear"
MODO_ALERTAR = "alertar"


@dataclass(frozen=True)
class Regra:
    """
    Uma regra medida a cada execução.

    limite_bloqueio / limite_alerta são percentuais de violação sobre os
    registros avaliados: o status é definido por comparação estrita
    (`percentual > limite`), então limite 0.0 significa tolerância zero.
    """

    nome: str
    descricao: str
    severidade: str
    limite_bloqueio: float | None = None
    limite_alerta: float | None = None


REGRAS = {
    regra.nome: regra
    for regra in [
        Regra(
            nome="tabela_vazia",
            descricao="Tabela Silver publicada sem nenhuma linha.",
            severidade=SEVERIDADE_BLOQUEANTE,
            limite_bloqueio=0.0,
        ),
        Regra(
            nome="chave_primaria_duplicada",
            descricao="Registros duplicados na chave primária declarada da tabela.",
            severidade=SEVERIDADE_BLOQUEANTE,
            limite_bloqueio=0.0,
        ),
        Regra(
            nome="nulo_em_campo_obrigatorio",
            descricao="Campo obrigatório nulo após a limpeza (indica falha da limpeza).",
            severidade=SEVERIDADE_BLOQUEANTE,
            limite_bloqueio=0.0,
        ),
        Regra(
            nome="percentual_fora_intervalo",
            descricao="Métrica percentual fora do intervalo [0,100].",
            severidade=SEVERIDADE_BLOQUEANTE,
            limite_bloqueio=5.0,
            limite_alerta=0.5,
        ),
        Regra(
            nome="campo_invalido",
            descricao=(
                "Campo reprovado nas demais validações de domínio "
                "(identificador vazio, peso não positivo, proficiência negativa)."
            ),
            severidade=SEVERIDADE_BLOQUEANTE,
            limite_bloqueio=5.0,
            limite_alerta=0.5,
        ),
        Regra(
            nome="chave_invalida_descartada",
            descricao=(
                "Linhas descartadas na limpeza Silver por chave primária ou campo "
                "obrigatório nulo — perda de dado, não deduplicação."
            ),
            severidade=SEVERIDADE_BLOQUEANTE,
            limite_bloqueio=5.0,
            limite_alerta=0.5,
        ),
        Regra(
            nome="duplicidade_removida",
            descricao=(
                "Linhas removidas por duplicidade na chave primária. Não é perda: "
                "dimensões (dim_escola, dim_municipio) são derivadas de tabelas de "
                "fato e a deduplicação é justamente o que as constrói — por isso a "
                "regra é de alerta, com limite alto, e não bloqueante."
            ),
            severidade=SEVERIDADE_ALERTA,
            limite_alerta=60.0,
        ),
        Regra(
            nome="metrica_ausente_fonte",
            descricao=(
                "Registros mantidos com métrica ausente na origem "
                "(flag_dado_ausente_fonte) — sinalizado, nunca descartado."
            ),
            severidade=SEVERIDADE_ALERTA,
            limite_alerta=30.0,
        ),
        Regra(
            nome="aumento_ausencia_safra_anterior",
            descricao=(
                "Aumento, em pontos percentuais, da ausência de métrica na fonte "
                "em relação à execução anterior registrada."
            ),
            severidade=SEVERIDADE_ALERTA,
            limite_alerta=10.0,
        ),
        Regra(
            nome="cobertura_territorial",
            descricao=(
                "Entidades territoriais ausentes na tabela Gold em relação ao "
                "universo esperado (27 UFs; municípios da dim_municipio). "
                "Ausência conhecida da fonte — AC e DF sem meta 2024, RR sem "
                "resultado até 2024 — cabe aqui: o objetivo é que a lacuna "
                "fique registrada e comparável, não que barre a execução."
            ),
            severidade=SEVERIDADE_ALERTA,
            limite_alerta=10.0,
        ),
        Regra(
            nome="queda_cobertura_safra_anterior",
            descricao=(
                "Entidades territoriais que existiam na execução anterior e "
                "sumiram nesta. Diferente da regra acima, aqui qualquer perda "
                "alerta: cobertura não deve regredir entre safras."
            ),
            severidade=SEVERIDADE_ALERTA,
            limite_alerta=0.0,
        ),
        Regra(
            nome="tabela_gold_vazia",
            descricao="Tabela Gold materializada sem nenhuma linha.",
            severidade=SEVERIDADE_ALERTA,
            limite_alerta=0.0,
        ),
    ]
}


def modo_execucao() -> str:
    """Modo corrente do gate de qualidade (`bloquear` por padrão)."""
    modo = os.getenv("QUALIDADE_MODO", MODO_BLOQUEAR).strip().lower()

    return modo if modo in {MODO_BLOQUEAR, MODO_ALERTAR} else MODO_BLOQUEAR
