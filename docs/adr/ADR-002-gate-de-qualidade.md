# ADR-002 — Validações que barram a execução, e histórico de qualidade persistido

- **Status**: aceito
- **Data**: 2026-09-02
- **Decisores**: time do Tech Challenge Fase 2

## Contexto

Até a entrega anterior, a qualidade de dados era **só sinalização**:

- `validar_percentual` criava `flag_<coluna>_valido` para cada métrica
  percentual, mas nada consumia a flag;
- `sinalizar_dado_ausente_fonte` marcava a métrica ausente na origem;
- `relatorio_ausencia_fonte` imprimia a distribuição no stdout;
- os notebooks de quality check exibiam os números na tela.

Duas consequências práticas:

1. **Nada interrompia a pipeline.** Se uma extração viesse com 100% dos
   percentuais fora de `[0,100]`, as flags registrariam, a Silver seria
   publicada, a Gold seria construída em cima e os dashboards mostrariam
   número errado com aparência de normalidade.
2. **Nada sobrevivia à execução.** Toda métrica morria no fim do processo. A
   pergunta que qualidade de dados existe para responder é comparativa — "os
   nulos de proficiência aumentaram desde a safra anterior?" — e sem
   persistência ela não tinha resposta.

## Decisão

**1. Separar sinalização de bloqueio.**

A decisão anterior continua válida onde ela é certa: ausência vinda da fonte é
informação legítima, é mantida e marcada com `flag_dado_ausente_fonte`, nunca
descartada nem imputada (ver a nota de governança em
`src/silver/qualidade.py`). O que muda é que **violação de regra estrutural
agora barra**: chave primária duplicada, campo obrigatório nulo, tabela vazia,
percentual fora de `[0,100]` e descarte excessivo de linhas por chave inválida
reprovam a execução acima do limite tolerado.

O catálogo de regras, com severidade e limite de cada uma, está em
`src/qualidade/regras.py`.

**2. Persistir toda métrica em `gold.metricas_qualidade`.**

Uma linha por execução/camada/tabela/regra, gravada em
`gold/metricas_qualidade/execution_date=<data>/`, no mesmo layout das demais
tabelas do lake. O dicionário da tabela está em
[`docs/dicionario_dados_gold.md`](../dicionario_dados_gold.md).

**3. Comparar com a safra anterior.**

Com o histórico gravado, cada execução lê a execução anterior e registra duas
regras comparativas: `aumento_ausencia_safra_anterior` (variação, em pontos
percentuais, da ausência de métrica por tabela) e
`queda_cobertura_safra_anterior` (entidades territoriais que existiam antes e
sumiram). É a resposta à pergunta comparativa que antes não tinha onde ser
respondida.

**4. Medir a cobertura territorial.**

A regra `cobertura_territorial` conta, por ano, quantas UFs e municípios cada
tabela Gold de fato publica contra o universo esperado. Ela nasceu de uma
auditoria dos dados: a Gold traz **24 das 27 UFs em 2024** — AC e DF só têm
meta a partir de 2025 na fonte e RR não tem resultado até 2024 — e nada disso
aparecia em lugar nenhum. Como a lacuna é da fonte, a regra é de alerta; o que
ela garante é que a lacuna fique registrada, com número, a cada execução. O
recorte avaliado vai na coluna `escopo` (`ano=2024`), e as lacunas conhecidas
estão descritas em [`docs/dicionario_dados_gold.md`](../dicionario_dados_gold.md),
na seção "Notas de cobertura dos dados".

## Onde o gate roda

Em `src/silver/processar_silver.py`, nesta ordem, que é deliberada:

1. transforma e limpa;
2. coleta as métricas;
3. **grava as métricas** — execução reprovada também deixa rastro auditável;
4. **avalia o gate** — `QualidadeInsuficienteError` interrompe aqui;
5. só então grava as tabelas Silver.

Uma safra reprovada, portanto, **não é publicada e não chega à Gold**. Como a
exceção sobe até o processo, o job Glue `silver-transformacoes` falha, e o
alerta de falha já implantado (EventBridge → SNS → e-mail, em
`infra/monitoring.tf`) avisa o time sem nenhuma infraestrutura nova.

A camada Gold registra a própria volumetria publicada e a cobertura
territorial na mesma partição de métricas, ao fim do processamento.

## Limites escolhidos

| Regra | Severidade | Limite | Por quê |
|---|---|---|---|
| `tabela_vazia` | bloqueante | 0% | Tabela sem linha é falha de extração, nunca resultado válido |
| `chave_primaria_duplicada` | bloqueante | 0% | A chave é declarada por nós; duplicata significa que o grão está errado |
| `nulo_em_campo_obrigatorio` | bloqueante | 0% | Após a limpeza deve ser zero por construção; se não for, a limpeza falhou |
| `percentual_fora_intervalo` | bloqueante | 5% | O cenário do feedback: percentual fora de `[0,100]` é dado corrompido |
| `campo_invalido` | bloqueante | 5% | Identificador vazio, peso não positivo, proficiência negativa |
| `chave_invalida_descartada` | bloqueante | 5% | Perda de linha por chave nula acima disso indica mudança de schema na origem |
| `duplicidade_removida` | alerta | 60% | **Não** é perda: `dim_escola` e `dim_municipio` nascem da deduplicação de tabelas de fato — barrar aqui reprovaria uma execução saudável |
| `metrica_ausente_fonte` | alerta | 30% | Ausência estrutural conhecida (RR com amostra reduzida, DF sem malha municipal) não pode barrar |
| `aumento_ausencia_safra_anterior` | alerta | 10 p.p. | Salto de ausência entre safras merece investigação, não interrupção |
| `cobertura_territorial` | alerta | 10% | UF ou município ausente do recorte de um ano — lacuna da fonte, mas hoje invisível no dashboard |
| `queda_cobertura_safra_anterior` | alerta | 0% | Cobertura não deve regredir: entidade que existia na safra anterior e sumiu vira alerta |
| `tabela_gold_vazia` | alerta | 0% | Uma Gold vazia com Silver aprovada é problema de junção, e o diagnóstico é humano |

A separação entre `chave_invalida_descartada` e `duplicidade_removida` veio de
um falso positivo real: a primeira versão media apenas "linhas removidas na
limpeza" e reprovou a execução por causa de `dim_escola`, que descarta 45% das
linhas na deduplicação **por construção**, já que é derivada do fato de alunos.

## Escape hatch

`QUALIDADE_MODO=alertar` registra as violações e segue em frente, para
investigação local. O padrão é `bloquear`, e nada no repositório define a
variável — quem quiser furar o gate precisa fazê-lo explicitamente.

## Consequências

- Uma safra ruim custa uma execução interrompida em vez de um dashboard
  errado. Considerando que os números alimentam priorização de política
  pública, o trade-off é claramente favorável.
- Limite mal calibrado pode reprovar execução saudável. Mitigação: os limites
  estão em um único módulo, o histórico gravado permite recalibrá-los com
  base em dados reais, e o modo `alertar` destrava uma investigação urgente.
- `gold.metricas_qualidade` cresce uma partição pequena (~185 linhas) por
  execução — irrelevante perto da Bronze, e coberto pelo mesmo bucket do
  [ADR-004](ADR-004-ciclo-de-vida-armazenamento.md).

## Verificação

`tests/test_qualidade.py` (12 testes) cobre os comportamentos que sustentam
esta decisão: extração com percentual fora do intervalo barra; deduplicação de
dimensão não barra; o histórico é gravado e a execução seguinte se compara com
a anterior; a cobertura territorial incompleta alerta sem barrar, e uma queda
de cobertura entre safras é detectada.

```bash
pytest tests/
```
