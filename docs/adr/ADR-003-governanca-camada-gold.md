# ADR-003 — Governança da camada Gold: papéis de tabela e consolidação das sobreposições

- **Status**: aceito
- **Data**: 2026-09-02
- **Decisores**: time do Tech Challenge Fase 2

## Contexto

A Gold chegou a 24 tabelas sem nenhum critério escrito sobre quando criar uma
tabela nova. O resultado foi sobreposição real entre três tabelas do mesmo
grão territorial:

| Tabela | Grão | Conteúdo |
|---|---|---|
| `indicador_meta_uf` | ano × UF × rede | Junção resultado + meta, todas as colunas das duas origens, `distancia_meta`, `status_meta` |
| `comparacao_meta_resultado_uf` | ano × UF × rede | **Projeção** de `indicador_meta_uf`: as mesmas linhas, um subconjunto das colunas, com `taxa_alfabetizacao` renomeada |
| `evolucao_meta_resultado_uf` | ano × UF × rede | `comparacao_meta_resultado_uf` **mais** `variacao_resultado_ano_anterior` e `variacao_meta_ano_anterior` |

Mesmo grão, mesma pergunta de negócio, três materializações — e
`comparacao_*` era um subconjunto estrito de colunas de `evolucao_*`. O mesmo
padrão se repetia no grão de município. Três tabelas custam três leituras a
manter em sincronia, três entradas no dicionário e três chances de um
dashboard escolher a errada.

## Decisão

**1. Toda tabela Gold tem um papel declarado.**

| Papel | O que é | Regra |
|---|---|---|
| **Base** | Junção canônica de um grão, com todas as colunas das origens | Uma por grão territorial. `indicador_meta_brasil` / `_uf` / `_municipio` |
| **Serving** | Recorte pronto para uma pergunta de consumo, derivado de uma base | Só existe se acrescentar coluna ou grão que a base não tem |
| **Observabilidade** | Métrica sobre a própria pipeline | `metricas_qualidade` ([ADR-002](ADR-002-gate-de-qualidade.md)) |

**Critério para criar tabela Gold nova**: ela precisa acrescentar coluna
calculada, mudar o grão ou integrar outra fonte. Reordenar, renomear ou
selecionar colunas de uma tabela existente **não** justifica materialização —
isso é uma consulta, ou uma view, não uma tabela.

**2. Consolidar a família meta × resultado em uma tabela de serving por grão.**

- `comparacao_meta_resultado_uf` e `comparacao_meta_resultado_municipio`
  deixam de ser materializadas: `evolucao_meta_resultado_*` já contém todas as
  colunas delas e mais as variações anuais.
- `comparacao_meta_resultado_brasil` passa a se chamar
  `evolucao_meta_resultado_brasil` e ganha as mesmas colunas de variação,
  fechando a simetria entre os três grãos.
- As três viraram uma implementação só, `processar_evolucao_meta_resultado`,
  parametrizada por grão (`src/gold/processar_gold.py`).

Resultado: de 24 para **22 tabelas analíticas**, mais `metricas_qualidade`.

| Grão | Base | Serving |
|---|---|---|
| Brasil | `indicador_meta_brasil` | `evolucao_meta_resultado_brasil` |
| UF | `indicador_meta_uf` | `evolucao_meta_resultado_uf` |
| Município | `indicador_meta_municipio` | `evolucao_meta_resultado_municipio` |

## Por que não consolidar mais

A auditoria olhou o catálogo inteiro; as demais proximidades **não** são
sobreposição, e mexer nelas pioraria a Gold:

- `ranking_uf_prioritaria` × `indicador_meta_uf`: o ranking muda o grão
  (só UFs abaixo da meta, ordenadas) e acrescenta a posição — é a tabela que
  a política pública consome direto.
- `ranking_territorial_prioridade` × `ranking_municipio_prioritario`: a
  primeira traz rankings nacional, regional e por UF; a segunda é o recorte
  executivo do top nacional.
- `indicador_alfabetizacao_municipio` × `indicador_meta_municipio`: a primeira
  integra outra fonte (Bolsa Família) e nomes de município — acréscimo real.
- `mapa_calor_territorial` × `desigualdade_territorial_uf`: grãos diferentes
  (município classificado por risco versus dispersão agregada por UF).
- `evolucao_alfabetizacao` × `evolucao_meta_resultado_brasil`: a primeira é
  série do resultado observado agregado por ano, sem meta; a segunda compara
  com a meta oficial por rede.

## Consequências

- Quem lia `comparacao_meta_resultado_uf` passa a ler
  `evolucao_meta_resultado_uf` — mesmas colunas, mais duas. Atualizados:
  `app/gold_catalog.py`, `docs/catalogo_tabelas_camadas.md` e
  `docs/dicionario_dados_gold.md`.
- Menos duas tabelas para reprocessar e gravar por execução, no S3 e no lake
  local.
- O critério de criação fica escrito: a próxima tabela Gold precisa passar
  pelo teste de "acrescenta coluna, grão ou fonte?".
- Partições antigas de `comparacao_*` continuam existindo em lakes já
  materializados e **não** são apagadas pelo código. O ciclo de vida do
  [ADR-004](ADR-004-ciclo-de-vida-armazenamento.md) cobre Bronze e Silver, não
  a Gold, então a limpeza é pontual e manual:
  `aws s3 rm s3://<bucket>/gold/comparacao_meta_resultado_uf/ --recursive`
  (idem `_municipio` e `_brasil`); no lake local, basta remover a pasta.
