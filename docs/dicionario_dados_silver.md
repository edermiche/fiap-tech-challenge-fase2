# Dicionário de Dados - Camada Silver

Este documento descreve as tabelas tratadas da camada Silver. A Silver contém dados padronizados, com chaves normalizadas, flags de qualidade e estruturas dimensionais e fato para apoiar a camada Gold e análises exploratórias.

**Total de tabelas documentadas:** 15

## Tabelas Documentadas

| Tabela | Descrição |
|---|---|
| `silver.dominio_regiao_uf` | Tabela de domínio que relaciona cada Unidade Federativa à respectiva região do Brasil. |
| `silver.dim_uf` | Dimensão de Unidades Federativas, enriquecida com a região do Brasil. |
| `silver.dim_municipio` | Dimensão de municípios utilizados nas análises da camada Silver. |
| `silver.dim_escola` | Dimensão de escolas observadas na base de alunos, vinculadas ao município. |
| `silver.fato_resultado_brasil` | Fato com indicadores nacionais observados de alfabetização por ano e rede. |
| `silver.fato_resultado_uf` | Fato com indicadores observados de alfabetização por UF, ano, série e rede. |
| `silver.fato_resultado_municipio` | Fato com indicadores observados de alfabetização por município, ano, série e rede. |
| `silver.fato_resultado_meta_uf` | Fato com resultados observados por UF oriundos da base de metas. |
| `silver.fato_resultado_meta_municipio` | Fato com resultados observados por município oriundos da base de metas. |
| `silver.fato_meta_anual_brasil` | Fato com metas nacionais de alfabetização, normalizadas de colunas para linhas. |
| `silver.fato_meta_anual_uf` | Fato com metas de alfabetização por UF, normalizadas de colunas para linhas. |
| `silver.fato_meta_anual_municipio` | Fato com metas de alfabetização por município, normalizadas de colunas para linhas. |
| `silver.fato_distribuicao_nivel_uf` | Fato com distribuição percentual de alunos por nível de alfabetização, agregada por UF. |
| `silver.fato_distribuicao_nivel_municipio` | Fato com distribuição percentual de alunos por nível de alfabetização, agregada por município. |
| `silver.fato_aluno_alfabetizacao` | Fato no nível do aluno, com presença, alfabetização, proficiência, peso e flags de qualidade. |

---

## silver.dominio_regiao_uf

**Descrição:** Tabela de domínio territorial com o mapeamento oficial das siglas das UFs para as cinco regiões do Brasil. Exemplo: `SP -> Sudeste`.

| Campo | Tipo esperado | Descrição |
|---|---|---|
| `sigla_uf` | `object` | Sigla da Unidade Federativa. |
| `regiao_brasil` | `object` | Região brasileira à qual a UF pertence: Norte, Nordeste, Centro-Oeste, Sudeste ou Sul. |
| `data_processamento_silver` | `object` | Data em que o registro foi processado na camada Silver. |

## silver.dim_uf

**Descrição:** Dimensão com cadastro das Unidades Federativas utilizadas nas análises. É usada para enriquecer fatos agregadas por UF com nome da UF e região do Brasil.

| Campo | Tipo esperado | Descrição |
|---|---|---|
| `sigla_uf` | `object` | Sigla da Unidade Federativa. |
| `sigla_uf_nome` | `object` | Nome da Unidade Federativa. |
| `regiao_brasil` | `object` | Região brasileira da UF, obtida a partir do domínio `silver.dominio_regiao_uf`. |
| `data_processamento_silver` | `object` | Data em que o registro foi processado na camada Silver. |

## silver.dim_municipio

**Descrição:** Dimensão com cadastro dos municípios usados nas tabelas fato municipais e escolares.

| Campo | Tipo esperado | Descrição |
|---|---|---|
| `id_municipio` | `object` | Código identificador do município. |
| `id_municipio_nome` | `object` | Nome do município. |
| `data_processamento_silver` | `object` | Data em que o registro foi processado na camada Silver. |

## silver.dim_escola

**Descrição:** Dimensão com cadastro básico das escolas observadas na base de alunos, preservando o vínculo da escola com o município.

| Campo | Tipo esperado | Descrição |
|---|---|---|
| `id_escola` | `object` | Código identificador da escola. |
| `id_municipio` | `object` | Código identificador do município ao qual a escola pertence. |
| `id_municipio_nome` | `object` | Nome do município ao qual a escola pertence. |
| `data_processamento_silver` | `object` | Data em que o registro foi processado na camada Silver. |

## silver.fato_resultado_brasil

**Descrição:** Tabela fato com indicadores nacionais observados de alfabetização, participação e respectivas flags de qualidade.

| Campo | Tipo esperado | Descrição |
|---|---|---|
| `ano` | `Int64` | Ano de referência do resultado observado. |
| `rede` | `object` | Rede de ensino considerada no indicador. |
| `taxa_alfabetizacao` | `float64` | Percentual ou taxa de alfabetização observada. |
| `percentual_participacao` | `float64` | Percentual de participação na avaliação. |
| `flag_taxa_alfabetizacao_valido` | `bool` | Indica se a taxa de alfabetização é nula ou está no intervalo válido de 0 a 100. |
| `flag_percentual_participacao_valido` | `bool` | Indica se o percentual de participação é nulo ou está no intervalo válido de 0 a 100. |
| `nivel_agregacao` | `object` | Nível territorial do registro, preenchido como `Brasil`. |
| `data_processamento_silver` | `object` | Data em que o registro foi processado na camada Silver. |

## silver.fato_resultado_uf

**Descrição:** Tabela fato com indicadores observados de alfabetização por UF, série, rede e ano.

| Campo | Tipo esperado | Descrição |
|---|---|---|
| `ano` | `Int64` | Ano de referência do resultado observado. |
| `sigla_uf` | `object` | Sigla da Unidade Federativa. |
| `serie` | `object` | Série escolar avaliada. |
| `rede` | `object` | Rede de ensino considerada no indicador. |
| `taxa_alfabetizacao` | `float64` | Percentual ou taxa de alfabetização observada. |
| `media_portugues` | `float64` | Média de desempenho em português. |
| `flag_taxa_alfabetizacao_valido` | `bool` | Indica se a taxa de alfabetização é nula ou está no intervalo válido de 0 a 100. |
| `data_processamento_silver` | `object` | Data em que o registro foi processado na camada Silver. |

## silver.fato_resultado_municipio

**Descrição:** Tabela fato com indicadores observados de alfabetização por município, série, rede e ano.

| Campo | Tipo esperado | Descrição |
|---|---|---|
| `ano` | `Int64` | Ano de referência do resultado observado. |
| `id_municipio` | `object` | Código identificador do município. |
| `serie` | `object` | Série escolar avaliada. |
| `rede` | `object` | Rede de ensino considerada no indicador. |
| `taxa_alfabetizacao` | `float64` | Percentual ou taxa de alfabetização observada. |
| `media_portugues` | `float64` | Média de desempenho em português. |
| `flag_taxa_alfabetizacao_valido` | `bool` | Indica se a taxa de alfabetização é nula ou está no intervalo válido de 0 a 100. |
| `data_processamento_silver` | `object` | Data em que o registro foi processado na camada Silver. |

## silver.fato_resultado_meta_uf

**Descrição:** Tabela fato com resultado observado de alfabetização por UF, vindo da base de metas e usado para comparação com metas anuais.

| Campo | Tipo esperado | Descrição |
|---|---|---|
| `ano` | `Int64` | Ano de referência do resultado observado. |
| `sigla_uf` | `object` | Sigla da Unidade Federativa. |
| `rede` | `object` | Rede de ensino considerada no indicador. |
| `taxa_alfabetizacao` | `float64` | Percentual ou taxa de alfabetização observada. |
| `percentual_participacao` | `float64` | Percentual de participação na avaliação. |
| `flag_taxa_alfabetizacao_valido` | `bool` | Indica se a taxa de alfabetização é nula ou está no intervalo válido de 0 a 100. |
| `flag_percentual_participacao_valido` | `bool` | Indica se o percentual de participação é nulo ou está no intervalo válido de 0 a 100. |
| `nivel_agregacao` | `object` | Nível territorial do registro, preenchido como `UF`. |
| `data_processamento_silver` | `object` | Data em que o registro foi processado na camada Silver. |

## silver.fato_resultado_meta_municipio

**Descrição:** Tabela fato com resultado observado de alfabetização por município, vindo da base de metas e usado para comparação com metas anuais municipais.

| Campo | Tipo esperado | Descrição |
|---|---|---|
| `ano` | `Int64` | Ano de referência do resultado observado. |
| `id_municipio` | `object` | Código identificador do município. |
| `rede` | `object` | Rede de ensino considerada no indicador. |
| `taxa_alfabetizacao` | `float64` | Percentual ou taxa de alfabetização observada. |
| `nivel_alfabetizacao` | `Int64` | Nível de alfabetização associado ao resultado municipal na base de metas. |
| `percentual_participacao` | `float64` | Percentual de participação na avaliação. |
| `nivel_agregacao` | `object` | Nível territorial do registro, preenchido como `Município`. |
| `data_processamento_silver` | `object` | Data em que o registro foi processado na camada Silver. |

## silver.fato_meta_anual_brasil

**Descrição:** Tabela fato com metas nacionais de alfabetização projetadas, com uma linha por ano de referência, rede e ano da meta.

| Campo | Tipo esperado | Descrição |
|---|---|---|
| `ano` | `Int64` | Ano de referência da série de metas. |
| `rede` | `object` | Rede de ensino considerada na meta. |
| `ano_meta` | `Int64` | Ano para o qual a meta de alfabetização foi definida. |
| `meta_alfabetizacao` | `float64` | Meta de alfabetização prevista para o `ano_meta`. |
| `flag_meta_alfabetizacao_valido` | `bool` | Indica se a meta de alfabetização é nula ou está no intervalo válido de 0 a 100. |
| `nivel_agregacao` | `object` | Nível territorial da meta, preenchido como `Brasil`. |
| `data_processamento_silver` | `object` | Data em que o registro foi processado na camada Silver. |

## silver.fato_meta_anual_uf

**Descrição:** Tabela fato com metas de alfabetização por UF, com uma linha por ano de referência, UF, rede e ano da meta.

| Campo | Tipo esperado | Descrição |
|---|---|---|
| `ano` | `Int64` | Ano de referência da série de metas. |
| `sigla_uf` | `object` | Sigla da Unidade Federativa. |
| `rede` | `object` | Rede de ensino considerada na meta. |
| `ano_meta` | `Int64` | Ano para o qual a meta de alfabetização foi definida. |
| `meta_alfabetizacao` | `float64` | Meta de alfabetização prevista para o `ano_meta`. |
| `flag_meta_alfabetizacao_valido` | `bool` | Indica se a meta de alfabetização é nula ou está no intervalo válido de 0 a 100. |
| `nivel_agregacao` | `object` | Nível territorial da meta, preenchido como `UF`. |
| `data_processamento_silver` | `object` | Data em que o registro foi processado na camada Silver. |

## silver.fato_meta_anual_municipio

**Descrição:** Tabela fato com metas de alfabetização por município, com uma linha por ano de referência, município, rede e ano da meta.

| Campo | Tipo esperado | Descrição |
|---|---|---|
| `ano` | `Int64` | Ano de referência da série de metas. |
| `id_municipio` | `object` | Código identificador do município. |
| `rede` | `object` | Rede de ensino considerada na meta. |
| `ano_meta` | `Int64` | Ano para o qual a meta de alfabetização foi definida. |
| `meta_alfabetizacao` | `float64` | Meta de alfabetização prevista para o `ano_meta`. |
| `nivel_agregacao` | `object` | Nível territorial da meta, preenchido como `Município`. |
| `data_processamento_silver` | `object` | Data em que o registro foi processado na camada Silver. |

## silver.fato_distribuicao_nivel_uf

**Descrição:** Tabela fato em formato longo com a distribuição percentual de alunos por nível de alfabetização, agregada por UF.

| Campo | Tipo esperado | Descrição |
|---|---|---|
| `ano` | `Int64` | Ano de referência da distribuição. |
| `sigla_uf` | `object` | Sigla da Unidade Federativa. |
| `serie` | `object` | Série escolar avaliada. |
| `rede` | `object` | Rede de ensino considerada na distribuição. |
| `nivel_alfabetizacao` | `Int64` | Nível de alfabetização, extraído das colunas originais `proporcao_aluno_nivel_0` a `proporcao_aluno_nivel_8`. |
| `proporcao_alunos` | `float64` | Proporção de alunos enquadrados no nível de alfabetização. |
| `flag_proporcao_alunos_valido` | `bool` | Indica se a proporção de alunos é nula ou está no intervalo válido de 0 a 100. |
| `data_processamento_silver` | `object` | Data em que o registro foi processado na camada Silver. |

## silver.fato_distribuicao_nivel_municipio

**Descrição:** Tabela fato em formato longo com a distribuição percentual de alunos por nível de alfabetização, agregada por município.

| Campo | Tipo esperado | Descrição |
|---|---|---|
| `ano` | `Int64` | Ano de referência da distribuição. |
| `id_municipio` | `object` | Código identificador do município. |
| `serie` | `object` | Série escolar avaliada. |
| `rede` | `object` | Rede de ensino considerada na distribuição. |
| `nivel_alfabetizacao` | `Int64` | Nível de alfabetização, extraído das colunas originais `proporcao_aluno_nivel_0` a `proporcao_aluno_nivel_8`. |
| `proporcao_alunos` | `float64` | Proporção de alunos enquadrados no nível de alfabetização. |
| `flag_proporcao_alunos_valido` | `bool` | Indica se a proporção de alunos é nula ou está no intervalo válido de 0 a 100. |
| `data_processamento_silver` | `object` | Data em que o registro foi processado na camada Silver. |

## silver.fato_aluno_alfabetizacao

**Descrição:** Tabela fato na menor granularidade da camada Silver, com uma linha por aluno avaliado e informações de presença, preenchimento, alfabetização, proficiência, peso e qualidade dos campos-chave.

| Campo | Tipo esperado | Descrição |
|---|---|---|
| `ano` | `Int64` | Ano de referência da avaliação do aluno. |
| `id_aluno` | `object` | Código identificador do aluno. |
| `id_escola` | `object` | Código identificador da escola do aluno. |
| `id_municipio` | `object` | Código identificador do município da escola do aluno. |
| `serie` | `object` | Série escolar avaliada. |
| `rede` | `object` | Rede de ensino da escola do aluno. |
| `caderno` | `object` | Identificação do caderno de avaliação aplicado ao aluno. |
| `presenca` | `object` | Indicador textual de presença do aluno na avaliação. |
| `preenchimento_caderno` | `object` | Indicador textual de preenchimento do caderno de avaliação. |
| `alfabetizado` | `object` | Indicador textual da condição de alfabetização do aluno. |
| `proficiencia` | `float64` | Valor de proficiência do aluno na avaliação. |
| `peso_aluno` | `float64` | Peso amostral ou ponderador associado ao aluno. |
| `flag_id_aluno_valido` | `bool` | Indica se o identificador do aluno está preenchido. |
| `flag_id_escola_valido` | `bool` | Indica se o identificador da escola está preenchido. |
| `flag_id_municipio_valido` | `bool` | Indica se o identificador do município está preenchido. |
| `flag_proficiencia_valida` | `bool` | Indica se a proficiência é nula ou possui valor maior ou igual a zero. |
| `flag_peso_aluno_valido` | `bool` | Indica se o peso do aluno é nulo ou possui valor maior que zero. |
| `flag_presenca_preenchida` | `bool` | Indica se o campo de presença está preenchido. |
| `flag_alfabetizado_preenchido` | `bool` | Indica se o campo `alfabetizado` está preenchido. |
| `data_processamento_silver` | `object` | Data em que o registro foi processado na camada Silver. |
