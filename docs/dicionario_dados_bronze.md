# Dicionário de Dados - Camada Bronze

Este documento apresenta o dicionário técnico inicial das tabelas da camada Bronze.

## Tabela: alunos

| coluna                | tipo_dado   |   qtd_nulos |   percentual_nulos |   qtd_valores_distintos | exemplo_valor                | descricao   | observacao   |
|:----------------------|:------------|------------:|-------------------:|------------------------:|:-----------------------------|:------------|:-------------|
| ano                   | Int64       |           0 |               0    |                       2 | 2023                         |             |              |
| id_municipio          | object      |           0 |               0    |                    5548 | 1301902                      |             |              |
| id_municipio_nome     | object      |           0 |               0    |                    5279 | Itacoatiara                  |             |              |
| id_escola             | object      |           0 |               0    |                   42811 | 60000747                     |             |              |
| id_aluno              | object      |           0 |               0    |                 2352328 | 13012277                     |             |              |
| caderno               | object      |           0 |               0    |                      22 | 1                            |             |              |
| serie                 | object      |           0 |               0    |                       1 | 2° ano do Ensino Fundamental |             |              |
| rede                  | object      |           0 |               0    |                       3 | Municipal                    |             |              |
| presenca              | object      |           0 |               0    |                       2 | Ausente                      |             |              |
| preenchimento_caderno | object      |           0 |               0    |                       2 | Prova não preenchida         |             |              |
| alfabetizado          | object      |           0 |               0    |                       2 | Não                          |             |              |
| proficiencia          | float64     |      513338 |              13.27 |                 1299544 | 677.8541717                  |             |              |
| peso_aluno            | float64     |      513338 |              13.27 |                   70528 | 0.2280726                    |             |              |

## Tabela: meta_alfabetizacao_brasil

| coluna                  | tipo_dado   |   qtd_nulos |   percentual_nulos |   qtd_valores_distintos | exemplo_valor   | descricao   | observacao   |
|:------------------------|:------------|------------:|-------------------:|------------------------:|:----------------|:------------|:-------------|
| ano                     | Int64       |           0 |                  0 |                       3 | 2025            |             |              |
| rede                    | object      |           0 |                  0 |                       1 | Pública         |             |              |
| taxa_alfabetizacao      | float64     |           0 |                  0 |                       3 | 66.0            |             |              |
| meta_alfabetizacao_2024 | float64     |           0 |                  0 |                       2 | 60.0            |             |              |
| meta_alfabetizacao_2025 | float64     |           0 |                  0 |                       2 | 64.0            |             |              |
| meta_alfabetizacao_2026 | float64     |           0 |                  0 |                       2 | 67.0            |             |              |
| meta_alfabetizacao_2027 | float64     |           0 |                  0 |                       2 | 71.0            |             |              |
| meta_alfabetizacao_2028 | float64     |           0 |                  0 |                       2 | 74.0            |             |              |
| meta_alfabetizacao_2029 | float64     |           0 |                  0 |                       2 | 77.0            |             |              |
| meta_alfabetizacao_2030 | float64     |           0 |                  0 |                       1 | 80.0            |             |              |
| percentual_participacao | float64     |           0 |                  0 |                       3 | 88.0            |             |              |

## Tabela: meta_alfabetizacao_municipio

| coluna                  | tipo_dado   |   qtd_nulos |   percentual_nulos |   qtd_valores_distintos | exemplo_valor    | descricao   | observacao   |
|:------------------------|:------------|------------:|-------------------:|------------------------:|:-----------------|:------------|:-------------|
| ano                     | Int64       |           0 |               0    |                       2 | 2023             |             |              |
| id_municipio            | object      |           0 |               0    |                    5352 | 4301750          |             |              |
| id_municipio_nome       | object      |           0 |               0    |                    5096 | Barão do Triunfo |             |              |
| rede                    | object      |           0 |               0    |                       1 | Municipal        |             |              |
| taxa_alfabetizacao      | float64     |         120 |               1.12 |                    3876 | 4.4              |             |              |
| meta_alfabetizacao_2024 | float64     |         240 |               2.24 |                    2745 | 7.94             |             |              |
| meta_alfabetizacao_2025 | float64     |           0 |               0    |                    2501 | 14.05            |             |              |
| meta_alfabetizacao_2026 | float64     |           0 |               0    |                    2284 | 23.65            |             |              |
| meta_alfabetizacao_2027 | float64     |           0 |               0    |                    1889 | 37.0             |             |              |
| meta_alfabetizacao_2028 | float64     |           0 |               0    |                    1387 | 52.68            |             |              |
| meta_alfabetizacao_2029 | float64     |           0 |               0    |                     755 | 67.85            |             |              |
| meta_alfabetizacao_2030 | float64     |           0 |               0    |                       1 | 80.0             |             |              |
| nivel_alfabetizacao     | Int64       |         120 |               1.12 |                       6 | 0                |             |              |
| percentual_participacao | float64     |         120 |               1.12 |                    2153 | 92.59            |             |              |

## Tabela: meta_alfabetizacao_uf

| coluna                  | tipo_dado   |   qtd_nulos |   percentual_nulos |   qtd_valores_distintos | exemplo_valor   | descricao   | observacao   |
|:------------------------|:------------|------------:|-------------------:|------------------------:|:----------------|:------------|:-------------|
| ano                     | Int64       |           0 |               0    |                       3 | 2024            |             |              |
| sigla_uf                | object      |           0 |               0    |                      27 | RR              |             |              |
| sigla_uf_nome           | object      |           0 |               0    |                      27 | Roraima         |             |              |
| rede                    | object      |           0 |               0    |                       1 | Pública         |             |              |
| taxa_alfabetizacao      | float64     |           4 |               4.94 |                      69 | 38.39           |             |              |
| meta_alfabetizacao_2024 | float64     |           9 |              11.11 |                      42 | 38.3            |             |              |
| meta_alfabetizacao_2025 | float64     |           3 |               3.7  |                      44 | 45.9            |             |              |
| meta_alfabetizacao_2026 | float64     |           2 |               2.47 |                      39 | 53.6            |             |              |
| meta_alfabetizacao_2027 | float64     |           2 |               2.47 |                      38 | 61.2            |             |              |
| meta_alfabetizacao_2028 | float64     |           2 |               2.47 |                      32 | 68.3            |             |              |
| meta_alfabetizacao_2029 | float64     |           2 |               2.47 |                      25 | 74.6            |             |              |
| meta_alfabetizacao_2030 | float64     |           2 |               2.47 |                       1 | 80.0            |             |              |
| percentual_participacao | float64     |           4 |               4.94 |                      62 | 92.84           |             |              |

## Tabela: municipio

| coluna                  | tipo_dado   |   qtd_nulos |   percentual_nulos |   qtd_valores_distintos | exemplo_valor                | descricao   | observacao   |
|:------------------------|:------------|------------:|-------------------:|------------------------:|:-----------------------------|:------------|:-------------|
| ano                     | Int64       |           0 |               0    |                       2 | 2023                         |             |              |
| id_municipio            | object      |           0 |               0    |                    5550 | 1100031                      |             |              |
| id_municipio_nome       | object      |           0 |               0    |                    5281 | Cabixi                       |             |              |
| serie                   | object      |           0 |               0    |                       1 | 2° ano do Ensino Fundamental |             |              |
| rede                    | object      |           0 |               0    |                       4 | Municipal                    |             |              |
| taxa_alfabetizacao      | float64     |           0 |               0    |                    6161 | 69.1                         |             |              |
| media_portugues         | float64     |           0 |               0    |                   13321 | 767.8763                     |             |              |
| proporcao_aluno_nivel_0 | float64     |       11547 |              48.12 |                     943 | 5.88                         |             |              |
| proporcao_aluno_nivel_1 | float64     |       11547 |              48.12 |                    1374 | 17.65                        |             |              |
| proporcao_aluno_nivel_2 | float64     |       11547 |              48.12 |                    1922 | 11.76                        |             |              |
| proporcao_aluno_nivel_3 | float64     |       11547 |              48.12 |                    2289 | 23.53                        |             |              |
| proporcao_aluno_nivel_4 | float64     |       11547 |              48.12 |                    2620 | 23.53                        |             |              |
| proporcao_aluno_nivel_5 | float64     |       11547 |              48.12 |                    2965 | 0.0                          |             |              |
| proporcao_aluno_nivel_6 | float64     |       11547 |              48.12 |                    2893 | 17.65                        |             |              |
| proporcao_aluno_nivel_7 | float64     |       11547 |              48.12 |                    2151 | 0.0                          |             |              |
| proporcao_aluno_nivel_8 | float64     |       11547 |              48.12 |                    1404 | 0.0                          |             |              |

## Tabela: uf

| coluna                  | tipo_dado   |   qtd_nulos |   percentual_nulos |   qtd_valores_distintos | exemplo_valor                | descricao   | observacao   |
|:------------------------|:------------|------------:|-------------------:|------------------------:|:-----------------------------|:------------|:-------------|
| ano                     | Int64       |           0 |               0    |                       2 | 2023                         |             |              |
| sigla_uf                | object      |           0 |               0    |                      25 | AM                           |             |              |
| sigla_uf_nome           | object      |           0 |               0    |                      25 | Amazonas                     |             |              |
| serie                   | object      |           0 |               0    |                       1 | 2° ano do Ensino Fundamental |             |              |
| rede                    | object      |           0 |               0    |                       4 | Municipal                    |             |              |
| taxa_alfabetizacao      | float64     |           0 |               0    |                     139 | 49.2                         |             |              |
| media_portugues         | float64     |           0 |               0    |                     140 | 733.6637                     |             |              |
| proporcao_aluno_nivel_0 | float64     |          70 |              48.28 |                      60 | 0.0                          |             |              |
| proporcao_aluno_nivel_1 | float64     |          70 |              48.28 |                      65 | 2.73                         |             |              |
| proporcao_aluno_nivel_2 | float64     |          70 |              48.28 |                      68 | 8.59                         |             |              |
| proporcao_aluno_nivel_3 | float64     |          70 |              48.28 |                      65 | 1.52                         |             |              |
| proporcao_aluno_nivel_4 | float64     |          70 |              48.28 |                      69 | 13.47                        |             |              |
| proporcao_aluno_nivel_5 | float64     |          70 |              48.28 |                      67 | 40.41                        |             |              |
| proporcao_aluno_nivel_6 | float64     |          70 |              48.28 |                      69 | 28.72                        |             |              |
| proporcao_aluno_nivel_7 | float64     |          70 |              48.28 |                      67 | 3.65                         |             |              |
| proporcao_aluno_nivel_8 | float64     |          70 |              48.28 |                      64 | 0.92                         |             |              |

