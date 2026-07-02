# Dicionário de Dados - Camada Gold

**Gerado em:** 2026-07-02 18:15:40

## Visão geral

A camada Gold contém tabelas analíticas finais derivadas da camada Silver, criadas para responder às perguntas de negócio relacionadas à alfabetização no Brasil.

**Total de tabelas Gold identificadas:** 7

## Tabelas identificadas

| Tabela | Arquivo mais recente |
|---|---|
| `gold.evolucao_alfabetizacao` | `../data/gold/evolucao_alfabetizacao/execution_date=2026-07-02/evolucao_alfabetizacao.parquet` |
| `gold.indicador_meta_brasil` | `../data/gold/indicador_meta_brasil/execution_date=2026-07-02/indicador_meta_brasil.parquet` |
| `gold.indicador_meta_municipio` | `../data/gold/indicador_meta_municipio/execution_date=2026-07-02/indicador_meta_municipio.parquet` |
| `gold.indicador_meta_uf` | `../data/gold/indicador_meta_uf/execution_date=2026-07-02/indicador_meta_uf.parquet` |
| `gold.ranking_municipio_prioritario` | `../data/gold/ranking_municipio_prioritario/execution_date=2026-07-02/ranking_municipio_prioritario.parquet` |
| `gold.ranking_uf_prioritaria` | `../data/gold/ranking_uf_prioritaria/execution_date=2026-07-02/ranking_uf_prioritaria.parquet` |
| `gold.resumo_status_meta` | `../data/gold/resumo_status_meta/execution_date=2026-07-02/resumo_status_meta.parquet` |

---

## gold.evolucao_alfabetizacao

**Descrição:** Tabela analítica consolidada para acompanhar a evolução da alfabetização por nível de agregação.

**Arquivo físico:** `../data/gold/evolucao_alfabetizacao/execution_date=2026-07-02/evolucao_alfabetizacao.parquet`

**Quantidade de linhas:** 5

**Quantidade de colunas:** 12

| Coluna | Tipo | Nulos | % Nulos | Valores distintos | Exemplo | Descrição |
|---|---|---:|---:|---:|---|---|
| `ano` | `Int64` | 0 | 0.0% | 2 | `2024` | Ano de referência do resultado observado. |
| `rede` | `object` | 0 | 0.0% | 2 | `Pública` | Rede de ensino. |
| `nivel_agregacao` | `object` | 0 | 0.0% | 3 | `Brasil` | Nível territorial da análise. |
| `taxa_alfabetizacao_media` | `float64` | 0 | 0.0% | 5 | `59.2` | Média da taxa de alfabetização observada no agrupamento. |
| `meta_alfabetizacao_media` | `float64` | 0 | 0.0% | 5 | `59.9` | Média da meta de alfabetização no agrupamento. |
| `distancia_media_meta` | `float64` | 0 | 0.0% | 5 | `-0.6999999999999957` | Média da distância entre taxa observada e meta de alfabetização. |
| `percentual_participacao_medio` | `float64` | 0 | 0.0% | 5 | `87.37` | Média do percentual de participação no agrupamento. |
| `total_registros` | `int64` | 0 | 0.0% | 3 | `1` | Quantidade de registros considerados no agrupamento. |
| `total_meta_atingida` | `int64` | 0 | 0.0% | 5 | `0` | Quantidade de registros com meta atingida. |
| `total_abaixo_meta` | `int64` | 0 | 0.0% | 5 | `1` | Quantidade de registros abaixo da meta. |
| `percentual_meta_atingida` | `float64` | 0 | 0.0% | 5 | `0.0` | Percentual de registros com meta atingida. |
| `data_processamento_gold` | `object` | 0 | 0.0% | 1 | `2026-07-02` | Data de processamento da camada Gold. |

## gold.indicador_meta_brasil

**Descrição:** Tabela analítica nacional que compara taxa de alfabetização observada com a meta do mesmo ano.

**Arquivo físico:** `../data/gold/indicador_meta_brasil/execution_date=2026-07-02/indicador_meta_brasil.parquet`

**Quantidade de linhas:** 2

**Quantidade de colunas:** 11

| Coluna | Tipo | Nulos | % Nulos | Valores distintos | Exemplo | Descrição |
|---|---|---:|---:|---:|---|---|
| `ano` | `Int64` | 0 | 0.0% | 2 | `2024` | Ano de referência do resultado observado. |
| `rede` | `object` | 0 | 0.0% | 1 | `Pública` | Rede de ensino. |
| `nivel_agregacao` | `object` | 0 | 0.0% | 1 | `Brasil` | Nível territorial da análise. |
| `taxa_alfabetizacao` | `float64` | 0 | 0.0% | 2 | `59.2` | Taxa de alfabetização observada. |
| `percentual_participacao` | `float64` | 0 | 0.0% | 2 | `87.37` | Percentual de participação na avaliação. |
| `ano_meta` | `Int64` | 0 | 0.0% | 2 | `2024` | Ano da meta comparada. |
| `meta_alfabetizacao` | `float64` | 0 | 0.0% | 2 | `59.9` | Meta de alfabetização prevista para o ano. |
| `distancia_meta` | `float64` | 0 | 0.0% | 2 | `-0.6999999999999957` | Diferença entre taxa observada e meta de alfabetização. |
| `flag_meta_atingida` | `bool` | 0 | 0.0% | 2 | `False` | Indica se a meta foi atingida. |
| `status_meta` | `object` | 0 | 0.0% | 2 | `Abaixo da meta` | Classificação textual do atingimento da meta. |
| `data_processamento_gold` | `object` | 0 | 0.0% | 1 | `2026-07-02` | Data de processamento da camada Gold. |

## gold.indicador_meta_municipio

**Descrição:** Tabela analítica por município que compara taxa de alfabetização observada com a meta do mesmo ano.

**Arquivo físico:** `../data/gold/indicador_meta_municipio/execution_date=2026-07-02/indicador_meta_municipio.parquet`

**Quantidade de linhas:** 5352

**Quantidade de colunas:** 13

| Coluna | Tipo | Nulos | % Nulos | Valores distintos | Exemplo | Descrição |
|---|---|---:|---:|---:|---|---|
| `ano` | `Int64` | 0 | 0.0% | 1 | `2024` | Ano de referência do resultado observado. |
| `id_municipio` | `object` | 0 | 0.0% | 5352 | `1100015` | Código identificador do município. |
| `id_municipio_nome` | `object` | 0 | 0.0% | 5096 | `Alta Floresta D'Oeste` | Nome do município. |
| `rede` | `object` | 0 | 0.0% | 1 | `Municipal` | Rede de ensino. |
| `nivel_agregacao` | `object` | 0 | 0.0% | 1 | `Município` | Nível territorial da análise. |
| `taxa_alfabetizacao` | `float64` | 0 | 0.0% | 3512 | `67.79` | Taxa de alfabetização observada. |
| `percentual_participacao` | `float64` | 0 | 0.0% | 1670 | `89.87` | Percentual de participação na avaliação. |
| `ano_meta` | `Int64` | 0 | 0.0% | 1 | `2024` | Ano da meta comparada. |
| `meta_alfabetizacao` | `float64` | 120 | 2.24% | 2745 | `67.08` | Meta de alfabetização prevista para o ano. |
| `distancia_meta` | `float64` | 120 | 2.24% | 4077 | `0.710000000000008` | Diferença entre taxa observada e meta de alfabetização. |
| `flag_meta_atingida` | `object` | 120 | 2.24% | 2 | `True` | Indica se a meta foi atingida. |
| `status_meta` | `object` | 0 | 0.0% | 3 | `Meta atingida` | Classificação textual do atingimento da meta. |
| `data_processamento_gold` | `object` | 0 | 0.0% | 1 | `2026-07-02` | Data de processamento da camada Gold. |

## gold.indicador_meta_uf

**Descrição:** Tabela analítica por UF que compara taxa de alfabetização observada com a meta do mesmo ano.

**Arquivo físico:** `../data/gold/indicador_meta_uf/execution_date=2026-07-02/indicador_meta_uf.parquet`

**Quantidade de linhas:** 54

**Quantidade de colunas:** 13

| Coluna | Tipo | Nulos | % Nulos | Valores distintos | Exemplo | Descrição |
|---|---|---:|---:|---:|---|---|
| `ano` | `Int64` | 0 | 0.0% | 2 | `2024` | Ano de referência do resultado observado. |
| `sigla_uf` | `object` | 0 | 0.0% | 27 | `AC` | Sigla da Unidade Federativa. |
| `sigla_uf_nome` | `object` | 4 | 7.41% | 25 | `Acre` | Nome da Unidade Federativa. |
| `rede` | `object` | 0 | 0.0% | 1 | `Pública` | Rede de ensino. |
| `nivel_agregacao` | `object` | 0 | 0.0% | 1 | `UF` | Nível territorial da análise. |
| `taxa_alfabetizacao` | `float64` | 1 | 1.85% | 46 | `51.38` | Taxa de alfabetização observada. |
| `percentual_participacao` | `float64` | 1 | 1.85% | 38 | `80.87` | Percentual de participação na avaliação. |
| `ano_meta` | `Int64` | 0 | 0.0% | 2 | `2024` | Ano da meta comparada. |
| `meta_alfabetizacao` | `float64` | 4 | 7.41% | 43 | `49.7` | Meta de alfabetização prevista para o ano. |
| `distancia_meta` | `float64` | 4 | 7.41% | 40 | `-1.0700000000000003` | Diferença entre taxa observada e meta de alfabetização. |
| `flag_meta_atingida` | `object` | 4 | 7.41% | 2 | `False` | Indica se a meta foi atingida. |
| `status_meta` | `object` | 0 | 0.0% | 3 | `Sem informação` | Classificação textual do atingimento da meta. |
| `data_processamento_gold` | `object` | 0 | 0.0% | 1 | `2026-07-02` | Data de processamento da camada Gold. |

## gold.ranking_municipio_prioritario

**Descrição:** Ranking de municípios priorizados conforme distância em relação à meta de alfabetização.

**Arquivo físico:** `../data/gold/ranking_municipio_prioritario/execution_date=2026-07-02/ranking_municipio_prioritario.parquet`

**Quantidade de linhas:** 2444

**Quantidade de colunas:** 11

| Coluna | Tipo | Nulos | % Nulos | Valores distintos | Exemplo | Descrição |
|---|---|---:|---:|---:|---|---|
| `ano` | `Int64` | 0 | 0.0% | 1 | `2024` | Ano de referência do resultado observado. |
| `posicao_prioridade` | `int64` | 0 | 0.0% | 2444 | `1` | Posição no ranking de priorização. |
| `id_municipio` | `object` | 0 | 0.0% | 2444 | `4320453` | Código identificador do município. |
| `id_municipio_nome` | `object` | 0 | 0.0% | 2379 | `Sério` | Nome do município. |
| `rede` | `object` | 0 | 0.0% | 1 | `Municipal` | Rede de ensino. |
| `taxa_alfabetizacao` | `float64` | 0 | 0.0% | 1830 | `11.1` | Taxa de alfabetização observada. |
| `meta_alfabetizacao` | `float64` | 0 | 0.0% | 1590 | `80.0` | Meta de alfabetização prevista para o ano. |
| `distancia_meta` | `float64` | 0 | 0.0% | 1938 | `-68.9` | Diferença entre taxa observada e meta de alfabetização. |
| `percentual_participacao` | `float64` | 0 | 0.0% | 1175 | `100.0` | Percentual de participação na avaliação. |
| `status_meta` | `object` | 0 | 0.0% | 1 | `Abaixo da meta` | Classificação textual do atingimento da meta. |
| `data_processamento_gold` | `object` | 0 | 0.0% | 1 | `2026-07-02` | Data de processamento da camada Gold. |

## gold.ranking_uf_prioritaria

**Descrição:** Ranking de UFs priorizadas conforme distância em relação à meta de alfabetização.

**Arquivo físico:** `../data/gold/ranking_uf_prioritaria/execution_date=2026-07-02/ranking_uf_prioritaria.parquet`

**Quantidade de linhas:** 19

**Quantidade de colunas:** 11

| Coluna | Tipo | Nulos | % Nulos | Valores distintos | Exemplo | Descrição |
|---|---|---:|---:|---:|---|---|
| `ano` | `Int64` | 0 | 0.0% | 2 | `2024` | Ano de referência do resultado observado. |
| `posicao_prioridade` | `int64` | 0 | 0.0% | 13 | `1` | Posição no ranking de priorização. |
| `sigla_uf` | `object` | 0 | 0.0% | 13 | `RS` | Sigla da Unidade Federativa. |
| `sigla_uf_nome` | `object` | 0 | 0.0% | 13 | `Rio Grande do Sul` | Nome da Unidade Federativa. |
| `rede` | `object` | 0 | 0.0% | 1 | `Pública` | Rede de ensino. |
| `taxa_alfabetizacao` | `float64` | 0 | 0.0% | 19 | `44.67` | Taxa de alfabetização observada. |
| `meta_alfabetizacao` | `float64` | 0 | 0.0% | 18 | `66.2` | Meta de alfabetização prevista para o ano. |
| `distancia_meta` | `float64` | 0 | 0.0% | 18 | `-21.53` | Diferença entre taxa observada e meta de alfabetização. |
| `percentual_participacao` | `float64` | 0 | 0.0% | 17 | `82.86` | Percentual de participação na avaliação. |
| `status_meta` | `object` | 0 | 0.0% | 1 | `Abaixo da meta` | Classificação textual do atingimento da meta. |
| `data_processamento_gold` | `object` | 0 | 0.0% | 1 | `2026-07-02` | Data de processamento da camada Gold. |

## gold.resumo_status_meta

**Descrição:** Tabela consolidada com a quantidade e percentual de registros por status da meta, ano e nível de agregação.

**Arquivo físico:** `../data/gold/resumo_status_meta/execution_date=2026-07-02/resumo_status_meta.parquet`

**Quantidade de linhas:** 11

**Quantidade de colunas:** 8

| Coluna | Tipo | Nulos | % Nulos | Valores distintos | Exemplo | Descrição |
|---|---|---:|---:|---:|---|---|
| `ano` | `Int64` | 0 | 0.0% | 2 | `2024` | Ano de referência do resultado observado. |
| `rede` | `object` | 0 | 0.0% | 2 | `Pública` | Rede de ensino. |
| `nivel_agregacao` | `object` | 0 | 0.0% | 3 | `Brasil` | Nível territorial da análise. |
| `status_meta` | `object` | 0 | 0.0% | 3 | `Abaixo da meta` | Classificação textual do atingimento da meta. |
| `quantidade` | `int64` | 0 | 0.0% | 9 | `1` | Quantidade de registros no agrupamento. |
| `total_registros` | `int64` | 0 | 0.0% | 3 | `1` | Quantidade de registros considerados no agrupamento. |
| `percentual_registros` | `float64` | 0 | 0.0% | 10 | `100.0` | Percentual de registros no agrupamento. |
| `data_processamento_gold` | `object` | 0 | 0.0% | 1 | `2026-07-02` | Data de processamento da camada Gold. |
