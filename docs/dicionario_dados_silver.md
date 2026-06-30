# Dicionário de Dados - Camada Silver

**Gerado em:** 2026-06-30 08:09:15

## Visão geral

Este documento descreve automaticamente as tabelas geradas na camada Silver do pipeline. A camada Silver contém dados tratados, padronizados e organizados para consumo analítico, preservando rastreabilidade com a camada Bronze.

**Total de tabelas Silver identificadas:** 12

## Tabelas identificadas

| Tabela | Arquivo mais recente |
|---|---|
| `silver.dim_escola` | `../data/silver/dim_escola/execution_date=2026-06-30/dim_escola.parquet` |
| `silver.dim_municipio` | `../data/silver/dim_municipio/execution_date=2026-06-30/dim_municipio.parquet` |
| `silver.dim_uf` | `../data/silver/dim_uf/execution_date=2026-06-30/dim_uf.parquet` |
| `silver.fato_aluno_alfabetizacao` | `../data/silver/fato_aluno_alfabetizacao/execution_date=2026-06-30/fato_aluno_alfabetizacao.parquet` |
| `silver.fato_distribuicao_nivel_municipio` | `../data/silver/fato_distribuicao_nivel_municipio/execution_date=2026-06-30/fato_distribuicao_nivel_municipio.parquet` |
| `silver.fato_distribuicao_nivel_uf` | `../data/silver/fato_distribuicao_nivel_uf/execution_date=2026-06-30/fato_distribuicao_nivel_uf.parquet` |
| `silver.fato_meta_anual_brasil` | `../data/silver/fato_meta_anual_brasil/execution_date=2026-06-30/fato_meta_anual_brasil.parquet` |
| `silver.fato_meta_anual_uf` | `../data/silver/fato_meta_anual_uf/execution_date=2026-06-30/fato_meta_anual_uf.parquet` |
| `silver.fato_resultado_brasil` | `../data/silver/fato_resultado_brasil/execution_date=2026-06-30/fato_resultado_brasil.parquet` |
| `silver.fato_resultado_meta_uf` | `../data/silver/fato_resultado_meta_uf/execution_date=2026-06-30/fato_resultado_meta_uf.parquet` |
| `silver.fato_resultado_municipio` | `../data/silver/fato_resultado_municipio/execution_date=2026-06-30/fato_resultado_municipio.parquet` |
| `silver.fato_resultado_uf` | `../data/silver/fato_resultado_uf/execution_date=2026-06-30/fato_resultado_uf.parquet` |

---

## silver.dim_escola

**Descrição:** Dimensão com cadastro básico das escolas observadas na base de alunos, vinculadas ao município.

**Arquivo físico:** `../data/silver/dim_escola/execution_date=2026-06-30/dim_escola.parquet`

**Quantidade de linhas:** 78.408

**Quantidade de colunas:** 4

| Coluna | Tipo | Categoria | Nulos | % Nulos | Valores distintos | Exemplo | Descrição |
|---|---|---|---:|---:|---:|---|---|
| `id_escola` | `object` | Chave / Identificador | 0 | 0.0% | 42811 | `60000156` | Código identificador da escola. |
| `id_municipio` | `object` | Chave / Identificador | 0 | 0.0% | 5548 | `1100015` | Código identificador do município. |
| `id_municipio_nome` | `object` | Chave / Identificador | 0 | 0.0% | 5279 | `Alta Floresta D'Oeste` | Nome do município. |
| `data_processamento_silver` | `object` | Temporal | 0 | 0.0% | 1 | `2026-06-30` | Data em que o registro foi processado na camada Silver. |

## silver.dim_municipio

**Descrição:** Dimensão com cadastro dos municípios utilizados nas análises da camada Silver.

**Arquivo físico:** `../data/silver/dim_municipio/execution_date=2026-06-30/dim_municipio.parquet`

**Quantidade de linhas:** 5.550

**Quantidade de colunas:** 3

| Coluna | Tipo | Categoria | Nulos | % Nulos | Valores distintos | Exemplo | Descrição |
|---|---|---|---:|---:|---:|---|---|
| `id_municipio` | `object` | Chave / Identificador | 0 | 0.0% | 5550 | `1100015` | Código identificador do município. |
| `id_municipio_nome` | `object` | Chave / Identificador | 0 | 0.0% | 5281 | `Alta Floresta D'Oeste` | Nome do município. |
| `data_processamento_silver` | `object` | Temporal | 0 | 0.0% | 1 | `2026-06-30` | Data em que o registro foi processado na camada Silver. |

## silver.dim_uf

**Descrição:** Dimensão com cadastro das Unidades Federativas utilizadas nas análises da camada Silver.

**Arquivo físico:** `../data/silver/dim_uf/execution_date=2026-06-30/dim_uf.parquet`

**Quantidade de linhas:** 25

**Quantidade de colunas:** 3

| Coluna | Tipo | Categoria | Nulos | % Nulos | Valores distintos | Exemplo | Descrição |
|---|---|---|---:|---:|---:|---|---|
| `sigla_uf` | `object` | Chave / Identificador | 0 | 0.0% | 25 | `AC` | Sigla da Unidade Federativa. |
| `sigla_uf_nome` | `object` | Atributo | 0 | 0.0% | 25 | `Acre` | Nome da Unidade Federativa. |
| `data_processamento_silver` | `object` | Temporal | 0 | 0.0% | 1 | `2026-06-30` | Data em que o registro foi processado na camada Silver. |

## silver.fato_aluno_alfabetizacao

**Descrição:** Tabela fato no nível do aluno, contendo informações de presença, alfabetização, proficiência e peso amostral.

**Arquivo físico:** `../data/silver/fato_aluno_alfabetizacao/execution_date=2026-06-30/fato_aluno_alfabetizacao.parquet`

**Quantidade de linhas:** 3.867.999

**Quantidade de colunas:** 20

| Coluna | Tipo | Categoria | Nulos | % Nulos | Valores distintos | Exemplo | Descrição |
|---|---|---|---:|---:|---:|---|---|
| `ano` | `Int64` | Temporal | 0 | 0.0% | 2 | `2023` | Ano de referência do registro. |
| `id_aluno` | `object` | Chave / Identificador | 0 | 0.0% | 2352328 | `11019569` | Código identificador do aluno. |
| `id_escola` | `object` | Chave / Identificador | 0 | 0.0% | 42811 | `60000156` | Código identificador da escola. |
| `id_municipio` | `object` | Chave / Identificador | 0 | 0.0% | 5548 | `1100015` | Código identificador do município. |
| `serie` | `object` | Atributo | 0 | 0.0% | 1 | `2° ano do Ensino Fundamental` | Série escolar avaliada. |
| `rede` | `object` | Atributo | 0 | 0.0% | 3 | `Municipal` | Rede de ensino. |
| `caderno` | `object` | Atributo | 0 | 0.0% | 22 | `8` | Identificação do caderno de avaliação aplicado ao aluno. |
| `presenca` | `object` | Atributo | 0 | 0.0% | 2 | `Presente` | Indicador de presença do aluno na avaliação. |
| `preenchimento_caderno` | `object` | Atributo | 0 | 0.0% | 2 | `Prova preenchida` | Indicador de preenchimento do caderno de avaliação. |
| `alfabetizado` | `object` | Atributo | 0 | 0.0% | 2 | `Não` | Indicador informado sobre a condição de alfabetização do aluno. |
| `proficiencia` | `float64` | Indicador / Métrica | 513338 | 13.27% | 1299544 | `679.6981` | Valor de proficiência do aluno. |
| `peso_aluno` | `float64` | Indicador / Métrica | 513338 | 13.27% | 70528 | `4.0` | Peso amostral ou ponderador associado ao aluno. |
| `flag_id_aluno_valido` | `bool` | Flag de qualidade | 0 | 0.0% | 1 | `True` | Flag que indica se o identificador do aluno está preenchido. |
| `flag_id_escola_valido` | `bool` | Flag de qualidade | 0 | 0.0% | 1 | `True` | Flag que indica se o identificador da escola está preenchido. |
| `flag_id_municipio_valido` | `bool` | Flag de qualidade | 0 | 0.0% | 1 | `True` | Flag que indica se o identificador do município está preenchido. |
| `flag_proficiencia_valida` | `bool` | Flag de qualidade | 0 | 0.0% | 1 | `True` | Flag que indica se a proficiência é nula ou possui valor maior ou igual a zero. |
| `flag_peso_aluno_valido` | `bool` | Flag de qualidade | 0 | 0.0% | 1 | `True` | Flag que indica se o peso do aluno é nulo ou possui valor maior que zero. |
| `flag_presenca_preenchida` | `bool` | Flag de qualidade | 0 | 0.0% | 1 | `True` | Flag que indica se o campo de presença está preenchido. |
| `flag_alfabetizado_preenchido` | `bool` | Flag de qualidade | 0 | 0.0% | 1 | `True` | Flag que indica se o campo alfabetizado está preenchido. |
| `data_processamento_silver` | `object` | Temporal | 0 | 0.0% | 1 | `2026-06-30` | Data em que o registro foi processado na camada Silver. |

## silver.fato_distribuicao_nivel_municipio

**Descrição:** Tabela fato com a distribuição dos alunos por nível de alfabetização, agregada por município.

**Arquivo físico:** `../data/silver/fato_distribuicao_nivel_municipio/execution_date=2026-06-30/fato_distribuicao_nivel_municipio.parquet`

**Quantidade de linhas:** 215.955

**Quantidade de colunas:** 8

| Coluna | Tipo | Categoria | Nulos | % Nulos | Valores distintos | Exemplo | Descrição |
|---|---|---|---:|---:|---:|---|---|
| `ano` | `Int64` | Temporal | 0 | 0.0% | 2 | `2023` | Ano de referência do registro. |
| `id_municipio` | `object` | Chave / Identificador | 0 | 0.0% | 5550 | `1100015` | Código identificador do município. |
| `serie` | `object` | Atributo | 0 | 0.0% | 1 | `2° ano do Ensino Fundamental` | Série escolar avaliada. |
| `rede` | `object` | Atributo | 0 | 0.0% | 4 | `Municipal` | Rede de ensino. |
| `nivel_alfabetizacao` | `Int64` | Atributo | 0 | 0.0% | 9 | `0` | Nível de alfabetização ou proficiência. |
| `proporcao_alunos` | `float64` | Indicador / Métrica | 103923 | 48.12% | 4346 | `1.41` | Proporção de alunos enquadrados no nível de alfabetização. |
| `flag_proporcao_alunos_valido` | `bool` | Flag de qualidade | 0 | 0.0% | 1 | `True` | Flag que indica se a proporção de alunos está dentro da regra de qualidade definida. |
| `data_processamento_silver` | `object` | Temporal | 0 | 0.0% | 1 | `2026-06-30` | Data em que o registro foi processado na camada Silver. |

## silver.fato_distribuicao_nivel_uf

**Descrição:** Tabela fato com a distribuição dos alunos por nível de alfabetização, agregada por UF.

**Arquivo físico:** `../data/silver/fato_distribuicao_nivel_uf/execution_date=2026-06-30/fato_distribuicao_nivel_uf.parquet`

**Quantidade de linhas:** 1.305

**Quantidade de colunas:** 8

| Coluna | Tipo | Categoria | Nulos | % Nulos | Valores distintos | Exemplo | Descrição |
|---|---|---|---:|---:|---:|---|---|
| `ano` | `Int64` | Temporal | 0 | 0.0% | 2 | `2023` | Ano de referência do registro. |
| `sigla_uf` | `object` | Chave / Identificador | 0 | 0.0% | 25 | `AL` | Sigla da Unidade Federativa. |
| `serie` | `object` | Atributo | 0 | 0.0% | 1 | `2° ano do Ensino Fundamental` | Série escolar avaliada. |
| `rede` | `object` | Atributo | 0 | 0.0% | 4 | `Estadual` | Rede de ensino. |
| `nivel_alfabetizacao` | `Int64` | Atributo | 0 | 0.0% | 9 | `0` | Nível de alfabetização ou proficiência. |
| `proporcao_alunos` | `float64` | Indicador / Métrica | 630 | 48.28% | 542 | `3.81` | Proporção de alunos enquadrados no nível de alfabetização. |
| `flag_proporcao_alunos_valido` | `bool` | Flag de qualidade | 0 | 0.0% | 1 | `True` | Flag que indica se a proporção de alunos está dentro da regra de qualidade definida. |
| `data_processamento_silver` | `object` | Temporal | 0 | 0.0% | 1 | `2026-06-30` | Data em que o registro foi processado na camada Silver. |

## silver.fato_meta_anual_brasil

**Descrição:** Tabela fato com metas nacionais de alfabetização transformadas de colunas para linhas.

**Arquivo físico:** `../data/silver/fato_meta_anual_brasil/execution_date=2026-06-30/fato_meta_anual_brasil.parquet`

**Quantidade de linhas:** 21

**Quantidade de colunas:** 7

| Coluna | Tipo | Categoria | Nulos | % Nulos | Valores distintos | Exemplo | Descrição |
|---|---|---|---:|---:|---:|---|---|
| `ano` | `Int64` | Temporal | 0 | 0.0% | 3 | `2023` | Ano de referência do registro. |
| `rede` | `object` | Atributo | 0 | 0.0% | 1 | `Pública` | Rede de ensino. |
| `ano_meta` | `Int64` | Temporal | 0 | 0.0% | 7 | `2024` | Ano da meta projetada de alfabetização. |
| `meta_alfabetizacao` | `float64` | Indicador / Métrica | 0 | 0.0% | 13 | `59.9` | Meta de alfabetização prevista para o ano_meta. |
| `flag_meta_alfabetizacao_valido` | `bool` | Flag de qualidade | 0 | 0.0% | 1 | `True` | Flag que indica se a meta de alfabetização está dentro da regra de qualidade definida. |
| `nivel_agregacao` | `object` | Atributo | 0 | 0.0% | 1 | `Brasil` | Nível territorial ou analítico da agregação. |
| `data_processamento_silver` | `object` | Temporal | 0 | 0.0% | 1 | `2026-06-30` | Data em que o registro foi processado na camada Silver. |

## silver.fato_meta_anual_uf

**Descrição:** Tabela fato com metas de alfabetização por UF transformadas de colunas para linhas.

**Arquivo físico:** `../data/silver/fato_meta_anual_uf/execution_date=2026-06-30/fato_meta_anual_uf.parquet`

**Quantidade de linhas:** 567

**Quantidade de colunas:** 8

| Coluna | Tipo | Categoria | Nulos | % Nulos | Valores distintos | Exemplo | Descrição |
|---|---|---|---:|---:|---:|---|---|
| `ano` | `Int64` | Temporal | 0 | 0.0% | 3 | `2023` | Ano de referência do registro. |
| `sigla_uf` | `object` | Chave / Identificador | 0 | 0.0% | 27 | `AC` | Sigla da Unidade Federativa. |
| `rede` | `object` | Atributo | 0 | 0.0% | 1 | `Pública` | Rede de ensino. |
| `ano_meta` | `Int64` | Temporal | 0 | 0.0% | 7 | `2024` | Ano da meta projetada de alfabetização. |
| `meta_alfabetizacao` | `float64` | Indicador / Métrica | 22 | 3.88% | 147 | `56.9` | Meta de alfabetização prevista para o ano_meta. |
| `flag_meta_alfabetizacao_valido` | `bool` | Flag de qualidade | 0 | 0.0% | 1 | `True` | Flag que indica se a meta de alfabetização está dentro da regra de qualidade definida. |
| `nivel_agregacao` | `object` | Atributo | 0 | 0.0% | 1 | `UF` | Nível territorial ou analítico da agregação. |
| `data_processamento_silver` | `object` | Temporal | 0 | 0.0% | 1 | `2026-06-30` | Data em que o registro foi processado na camada Silver. |

## silver.fato_resultado_brasil

**Descrição:** Tabela fato com indicadores nacionais de alfabetização por ano e rede.

**Arquivo físico:** `../data/silver/fato_resultado_brasil/execution_date=2026-06-30/fato_resultado_brasil.parquet`

**Quantidade de linhas:** 3

**Quantidade de colunas:** 8

| Coluna | Tipo | Categoria | Nulos | % Nulos | Valores distintos | Exemplo | Descrição |
|---|---|---|---:|---:|---:|---|---|
| `ano` | `Int64` | Temporal | 0 | 0.0% | 3 | `2023` | Ano de referência do registro. |
| `rede` | `object` | Atributo | 0 | 0.0% | 1 | `Pública` | Rede de ensino. |
| `taxa_alfabetizacao` | `float64` | Indicador / Métrica | 0 | 0.0% | 3 | `55.9` | Percentual ou taxa de alfabetização observada. |
| `percentual_participacao` | `float64` | Indicador / Métrica | 0 | 0.0% | 3 | `86.0` | Percentual de participação na avaliação. |
| `flag_taxa_alfabetizacao_valido` | `bool` | Flag de qualidade | 0 | 0.0% | 1 | `True` | Flag que indica se a taxa de alfabetização está dentro da regra de qualidade definida. |
| `flag_percentual_participacao_valido` | `bool` | Flag de qualidade | 0 | 0.0% | 1 | `True` | Flag que indica se o percentual de participação está dentro da regra de qualidade definida. |
| `nivel_agregacao` | `object` | Atributo | 0 | 0.0% | 1 | `Brasil` | Nível territorial ou analítico da agregação. |
| `data_processamento_silver` | `object` | Temporal | 0 | 0.0% | 1 | `2026-06-30` | Data em que o registro foi processado na camada Silver. |

## silver.fato_resultado_meta_uf

**Descrição:** Tabela fato com resultados observados de alfabetização por ano, UF e rede, oriundos da base de metas.

**Arquivo físico:** `../data/silver/fato_resultado_meta_uf/execution_date=2026-06-30/fato_resultado_meta_uf.parquet`

**Quantidade de linhas:** 81

**Quantidade de colunas:** 9

| Coluna | Tipo | Categoria | Nulos | % Nulos | Valores distintos | Exemplo | Descrição |
|---|---|---|---:|---:|---:|---|---|
| `ano` | `Int64` | Temporal | 0 | 0.0% | 3 | `2023` | Ano de referência do registro. |
| `sigla_uf` | `object` | Chave / Identificador | 0 | 0.0% | 27 | `AC` | Sigla da Unidade Federativa. |
| `rede` | `object` | Atributo | 0 | 0.0% | 1 | `Pública` | Rede de ensino. |
| `taxa_alfabetizacao` | `float64` | Indicador / Métrica | 4 | 4.94% | 69 | `43.88` | Percentual ou taxa de alfabetização observada. |
| `percentual_participacao` | `float64` | Indicador / Métrica | 4 | 4.94% | 62 | `92.36` | Percentual de participação na avaliação. |
| `flag_taxa_alfabetizacao_valido` | `bool` | Flag de qualidade | 0 | 0.0% | 1 | `True` | Flag que indica se a taxa de alfabetização está dentro da regra de qualidade definida. |
| `flag_percentual_participacao_valido` | `bool` | Flag de qualidade | 0 | 0.0% | 1 | `True` | Flag que indica se o percentual de participação está dentro da regra de qualidade definida. |
| `nivel_agregacao` | `object` | Atributo | 0 | 0.0% | 1 | `UF` | Nível territorial ou analítico da agregação. |
| `data_processamento_silver` | `object` | Temporal | 0 | 0.0% | 1 | `2026-06-30` | Data em que o registro foi processado na camada Silver. |

## silver.fato_resultado_municipio

**Descrição:** Tabela fato com indicadores de alfabetização agregados por ano, município, série e rede.

**Arquivo físico:** `../data/silver/fato_resultado_municipio/execution_date=2026-06-30/fato_resultado_municipio.parquet`

**Quantidade de linhas:** 23.995

**Quantidade de colunas:** 8

| Coluna | Tipo | Categoria | Nulos | % Nulos | Valores distintos | Exemplo | Descrição |
|---|---|---|---:|---:|---:|---|---|
| `ano` | `Int64` | Temporal | 0 | 0.0% | 2 | `2023` | Ano de referência do registro. |
| `id_municipio` | `object` | Chave / Identificador | 0 | 0.0% | 5550 | `1100015` | Código identificador do município. |
| `serie` | `object` | Atributo | 0 | 0.0% | 1 | `2° ano do Ensino Fundamental` | Série escolar avaliada. |
| `rede` | `object` | Atributo | 0 | 0.0% | 4 | `Municipal` | Rede de ensino. |
| `taxa_alfabetizacao` | `float64` | Indicador / Métrica | 0 | 0.0% | 6161 | `64.55` | Percentual ou taxa de alfabetização observada. |
| `media_portugues` | `float64` | Indicador / Métrica | 0 | 0.0% | 13321 | `758.3304` | Média de desempenho em português. |
| `flag_taxa_alfabetizacao_valido` | `bool` | Flag de qualidade | 0 | 0.0% | 1 | `True` | Flag que indica se a taxa de alfabetização está dentro da regra de qualidade definida. |
| `data_processamento_silver` | `object` | Temporal | 0 | 0.0% | 1 | `2026-06-30` | Data em que o registro foi processado na camada Silver. |

## silver.fato_resultado_uf

**Descrição:** Tabela fato com indicadores de alfabetização agregados por ano, UF, série e rede.

**Arquivo físico:** `../data/silver/fato_resultado_uf/execution_date=2026-06-30/fato_resultado_uf.parquet`

**Quantidade de linhas:** 145

**Quantidade de colunas:** 8

| Coluna | Tipo | Categoria | Nulos | % Nulos | Valores distintos | Exemplo | Descrição |
|---|---|---|---:|---:|---:|---|---|
| `ano` | `Int64` | Temporal | 0 | 0.0% | 2 | `2023` | Ano de referência do registro. |
| `sigla_uf` | `object` | Chave / Identificador | 0 | 0.0% | 25 | `AL` | Sigla da Unidade Federativa. |
| `serie` | `object` | Atributo | 0 | 0.0% | 1 | `2° ano do Ensino Fundamental` | Série escolar avaliada. |
| `rede` | `object` | Atributo | 0 | 0.0% | 4 | `Estadual` | Rede de ensino. |
| `taxa_alfabetizacao` | `float64` | Indicador / Métrica | 0 | 0.0% | 139 | `38.65` | Percentual ou taxa de alfabetização observada. |
| `media_portugues` | `float64` | Indicador / Métrica | 0 | 0.0% | 140 | `724.7993` | Média de desempenho em português. |
| `flag_taxa_alfabetizacao_valido` | `bool` | Flag de qualidade | 0 | 0.0% | 1 | `True` | Flag que indica se a taxa de alfabetização está dentro da regra de qualidade definida. |
| `data_processamento_silver` | `object` | Temporal | 0 | 0.0% | 1 | `2026-06-30` | Data em que o registro foi processado na camada Silver. |
