# Insumos de Modelagem - Camada Bronze## Resumo das Tabelas| tabela                       |   qtd_linhas |   qtd_colunas |   qtd_duplicados |   percentual_duplicados |
|:-----------------------------|-------------:|--------------:|-----------------:|------------------------:|
| alunos                       |      3867999 |            13 |                0 |                       0 |
| meta_alfabetizacao_brasil    |            3 |            11 |                0 |                       0 |
| meta_alfabetizacao_municipio |        10704 |            14 |                0 |                       0 |
| meta_alfabetizacao_uf        |           81 |            13 |                0 |                       0 |
| municipio                    |        23995 |            16 |                0 |                       0 |
| uf                           |          145 |            16 |                0 |                       0 |## Possíveis Chaves Primárias Simples| tabela                    | coluna_candidata        | tipo    |   qtd_linhas |   qtd_distintos | motivo                                |
|:--------------------------|:------------------------|:--------|-------------:|----------------:|:--------------------------------------|
| meta_alfabetizacao_brasil | ano                     | Int64   |            3 |               3 | Coluna sem nulos e com valores únicos |
| meta_alfabetizacao_brasil | taxa_alfabetizacao      | float64 |            3 |               3 | Coluna sem nulos e com valores únicos |
| meta_alfabetizacao_brasil | percentual_participacao | float64 |            3 |               3 | Coluna sem nulos e com valores únicos |## Possíveis Chaves Compostas| tabela                       | colunas_candidatas          |   qtd_linhas |   qtd_distintos_combinacao | motivo                                    |
|:-----------------------------|:----------------------------|-------------:|---------------------------:|:------------------------------------------|
| alunos                       | ano, id_aluno               |      3867999 |                    3867999 | Combinação sem nulos e com valores únicos |
| alunos                       | ano, id_municipio, id_aluno |      3867999 |                    3867999 | Combinação sem nulos e com valores únicos |
| alunos                       | ano, rede, id_aluno         |      3867999 |                    3867999 | Combinação sem nulos e com valores únicos |
| alunos                       | ano, serie, id_aluno        |      3867999 |                    3867999 | Combinação sem nulos e com valores únicos |
| alunos                       | ano, id_escola, id_aluno    |      3867999 |                    3867999 | Combinação sem nulos e com valores únicos |
| meta_alfabetizacao_brasil    | ano, rede                   |            3 |                          3 | Combinação sem nulos e com valores únicos |
| meta_alfabetizacao_municipio | ano, id_municipio           |        10704 |                      10704 | Combinação sem nulos e com valores únicos |
| meta_alfabetizacao_municipio | ano, id_municipio, rede     |        10704 |                      10704 | Combinação sem nulos e com valores únicos |
| meta_alfabetizacao_uf        | ano, sigla_uf               |           81 |                         81 | Combinação sem nulos e com valores únicos |
| meta_alfabetizacao_uf        | ano, sigla_uf, rede         |           81 |                         81 | Combinação sem nulos e com valores únicos |
| municipio                    | ano, id_municipio, rede     |        23995 |                      23995 | Combinação sem nulos e com valores únicos |
| uf                           | ano, sigla_uf, rede         |          145 |                        145 | Combinação sem nulos e com valores únicos |## Possíveis Relacionamentos| tabela_origem                | tabela_destino               | chave        |   qtd_valores_origem |   qtd_valores_destino |   percentual_cobertura_origem_no_destino |
|:-----------------------------|:-----------------------------|:-------------|---------------------:|----------------------:|-----------------------------------------:|
| alunos                       | meta_alfabetizacao_brasil    | ano          |                    2 |                     3 |                                   100    |
| alunos                       | meta_alfabetizacao_brasil    | rede         |                    3 |                     1 |                                     0    |
| alunos                       | meta_alfabetizacao_municipio | id_municipio |                 5548 |                  5352 |                                    96.47 |
| alunos                       | meta_alfabetizacao_municipio | ano          |                    2 |                     2 |                                   100    |
| alunos                       | meta_alfabetizacao_municipio | rede         |                    3 |                     1 |                                    33.33 |
| alunos                       | meta_alfabetizacao_uf        | ano          |                    2 |                     3 |                                   100    |
| alunos                       | meta_alfabetizacao_uf        | rede         |                    3 |                     1 |                                     0    |
| alunos                       | municipio                    | id_municipio |                 5548 |                  5550 |                                    99.98 |
| alunos                       | municipio                    | ano          |                    2 |                     2 |                                   100    |
| alunos                       | municipio                    | rede         |                    3 |                     4 |                                    66.67 |
| alunos                       | municipio                    | serie        |                    1 |                     1 |                                   100    |
| alunos                       | uf                           | ano          |                    2 |                     2 |                                   100    |
| alunos                       | uf                           | rede         |                    3 |                     4 |                                    66.67 |
| alunos                       | uf                           | serie        |                    1 |                     1 |                                   100    |
| meta_alfabetizacao_brasil    | alunos                       | ano          |                    3 |                     2 |                                    66.67 |
| meta_alfabetizacao_brasil    | alunos                       | rede         |                    1 |                     3 |                                     0    |
| meta_alfabetizacao_brasil    | meta_alfabetizacao_municipio | ano          |                    3 |                     2 |                                    66.67 |
| meta_alfabetizacao_brasil    | meta_alfabetizacao_municipio | rede         |                    1 |                     1 |                                     0    |
| meta_alfabetizacao_brasil    | meta_alfabetizacao_uf        | ano          |                    3 |                     3 |                                   100    |
| meta_alfabetizacao_brasil    | meta_alfabetizacao_uf        | rede         |                    1 |                     1 |                                   100    |
| meta_alfabetizacao_brasil    | municipio                    | ano          |                    3 |                     2 |                                    66.67 |
| meta_alfabetizacao_brasil    | municipio                    | rede         |                    1 |                     4 |                                     0    |
| meta_alfabetizacao_brasil    | uf                           | ano          |                    3 |                     2 |                                    66.67 |
| meta_alfabetizacao_brasil    | uf                           | rede         |                    1 |                     4 |                                     0    |
| meta_alfabetizacao_municipio | alunos                       | id_municipio |                 5352 |                  5548 |                                   100    |
| meta_alfabetizacao_municipio | alunos                       | ano          |                    2 |                     2 |                                   100    |
| meta_alfabetizacao_municipio | alunos                       | rede         |                    1 |                     3 |                                   100    |
| meta_alfabetizacao_municipio | meta_alfabetizacao_brasil    | ano          |                    2 |                     3 |                                   100    |
| meta_alfabetizacao_municipio | meta_alfabetizacao_brasil    | rede         |                    1 |                     1 |                                     0    |
| meta_alfabetizacao_municipio | meta_alfabetizacao_uf        | ano          |                    2 |                     3 |                                   100    |
| meta_alfabetizacao_municipio | meta_alfabetizacao_uf        | rede         |                    1 |                     1 |                                     0    |
| meta_alfabetizacao_municipio | municipio                    | id_municipio |                 5352 |                  5550 |                                   100    |
| meta_alfabetizacao_municipio | municipio                    | ano          |                    2 |                     2 |                                   100    |
| meta_alfabetizacao_municipio | municipio                    | rede         |                    1 |                     4 |                                   100    |
| meta_alfabetizacao_municipio | uf                           | ano          |                    2 |                     2 |                                   100    |
| meta_alfabetizacao_municipio | uf                           | rede         |                    1 |                     4 |                                   100    |
| meta_alfabetizacao_uf        | alunos                       | ano          |                    3 |                     2 |                                    66.67 |
| meta_alfabetizacao_uf        | alunos                       | rede         |                    1 |                     3 |                                     0    |
| meta_alfabetizacao_uf        | meta_alfabetizacao_brasil    | ano          |                    3 |                     3 |                                   100    |
| meta_alfabetizacao_uf        | meta_alfabetizacao_brasil    | rede         |                    1 |                     1 |                                   100    |
| meta_alfabetizacao_uf        | meta_alfabetizacao_municipio | ano          |                    3 |                     2 |                                    66.67 |
| meta_alfabetizacao_uf        | meta_alfabetizacao_municipio | rede         |                    1 |                     1 |                                     0    |
| meta_alfabetizacao_uf        | municipio                    | ano          |                    3 |                     2 |                                    66.67 |
| meta_alfabetizacao_uf        | municipio                    | rede         |                    1 |                     4 |                                     0    |
| meta_alfabetizacao_uf        | uf                           | sigla_uf     |                   27 |                    25 |                                    92.59 |
| meta_alfabetizacao_uf        | uf                           | ano          |                    3 |                     2 |                                    66.67 |
| meta_alfabetizacao_uf        | uf                           | rede         |                    1 |                     4 |                                     0    |
| municipio                    | alunos                       | id_municipio |                 5550 |                  5548 |                                    99.95 |
| municipio                    | alunos                       | ano          |                    2 |                     2 |                                   100    |
| municipio                    | alunos                       | rede         |                    4 |                     3 |                                    50    |
| municipio                    | alunos                       | serie        |                    1 |                     1 |                                   100    |
| municipio                    | meta_alfabetizacao_brasil    | ano          |                    2 |                     3 |                                   100    |
| municipio                    | meta_alfabetizacao_brasil    | rede         |                    4 |                     1 |                                     0    |
| municipio                    | meta_alfabetizacao_municipio | id_municipio |                 5550 |                  5352 |                                    96.43 |
| municipio                    | meta_alfabetizacao_municipio | ano          |                    2 |                     2 |                                   100    |
| municipio                    | meta_alfabetizacao_municipio | rede         |                    4 |                     1 |                                    25    |
| municipio                    | meta_alfabetizacao_uf        | ano          |                    2 |                     3 |                                   100    |
| municipio                    | meta_alfabetizacao_uf        | rede         |                    4 |                     1 |                                     0    |
| municipio                    | uf                           | ano          |                    2 |                     2 |                                   100    |
| municipio                    | uf                           | rede         |                    4 |                     4 |                                   100    |
| municipio                    | uf                           | serie        |                    1 |                     1 |                                   100    |
| uf                           | alunos                       | ano          |                    2 |                     2 |                                   100    |
| uf                           | alunos                       | rede         |                    4 |                     3 |                                    50    |
| uf                           | alunos                       | serie        |                    1 |                     1 |                                   100    |
| uf                           | meta_alfabetizacao_brasil    | ano          |                    2 |                     3 |                                   100    |
| uf                           | meta_alfabetizacao_brasil    | rede         |                    4 |                     1 |                                     0    |
| uf                           | meta_alfabetizacao_municipio | ano          |                    2 |                     2 |                                   100    |
| uf                           | meta_alfabetizacao_municipio | rede         |                    4 |                     1 |                                    25    |
| uf                           | meta_alfabetizacao_uf        | sigla_uf     |                   25 |                    27 |                                   100    |
| uf                           | meta_alfabetizacao_uf        | ano          |                    2 |                     3 |                                   100    |
| uf                           | meta_alfabetizacao_uf        | rede         |                    4 |                     1 |                                     0    |
| uf                           | municipio                    | ano          |                    2 |                     2 |                                   100    |
| uf                           | municipio                    | rede         |                    4 |                     4 |                                   100    |
| uf                           | municipio                    | serie        |                    1 |                     1 |                                   100    |## Backlog Inicial para Silver| tabela                       | coluna                  | tipo_problema       | descricao                                        | acao_sugerida                                           |
|:-----------------------------|:------------------------|:--------------------|:-------------------------------------------------|:--------------------------------------------------------|
| alunos                       | id_municipio            | tipo_texto_generico | Coluna está como object.                         | Padronizar para string ou converter para tipo adequado. |
| alunos                       | id_municipio            | validacao_chave     | Campo aparenta ser chave de relacionamento.      | Validar integridade referencial entre tabelas.          |
| alunos                       | id_municipio_nome       | tipo_texto_generico | Coluna está como object.                         | Padronizar para string ou converter para tipo adequado. |
| alunos                       | id_municipio_nome       | validacao_chave     | Campo aparenta ser chave de relacionamento.      | Validar integridade referencial entre tabelas.          |
| alunos                       | id_escola               | tipo_texto_generico | Coluna está como object.                         | Padronizar para string ou converter para tipo adequado. |
| alunos                       | id_escola               | validacao_chave     | Campo aparenta ser chave de relacionamento.      | Validar integridade referencial entre tabelas.          |
| alunos                       | id_aluno                | tipo_texto_generico | Coluna está como object.                         | Padronizar para string ou converter para tipo adequado. |
| alunos                       | id_aluno                | validacao_chave     | Campo aparenta ser chave de relacionamento.      | Validar integridade referencial entre tabelas.          |
| alunos                       | caderno                 | tipo_texto_generico | Coluna está como object.                         | Padronizar para string ou converter para tipo adequado. |
| alunos                       | serie                   | tipo_texto_generico | Coluna está como object.                         | Padronizar para string ou converter para tipo adequado. |
| alunos                       | rede                    | tipo_texto_generico | Coluna está como object.                         | Padronizar para string ou converter para tipo adequado. |
| alunos                       | presenca                | tipo_texto_generico | Coluna está como object.                         | Padronizar para string ou converter para tipo adequado. |
| alunos                       | preenchimento_caderno   | tipo_texto_generico | Coluna está como object.                         | Padronizar para string ou converter para tipo adequado. |
| alunos                       | alfabetizado            | tipo_texto_generico | Coluna está como object.                         | Padronizar para string ou converter para tipo adequado. |
| alunos                       | proficiencia            | valor_nulo          | Coluna possui 13.27% de valores nulos.           | Avaliar preenchimento, remoção ou manutenção como nulo. |
| alunos                       | peso_aluno              | valor_nulo          | Coluna possui 13.27% de valores nulos.           | Avaliar preenchimento, remoção ou manutenção como nulo. |
| meta_alfabetizacao_brasil    | rede                    | tipo_texto_generico | Coluna está como object.                         | Padronizar para string ou converter para tipo adequado. |
| meta_alfabetizacao_brasil    | taxa_alfabetizacao      | validacao_intervalo | Campo percentual/proporcional deve ser validado. | Validar se os valores estão no intervalo esperado.      |
| meta_alfabetizacao_brasil    | percentual_participacao | validacao_intervalo | Campo percentual/proporcional deve ser validado. | Validar se os valores estão no intervalo esperado.      |
| meta_alfabetizacao_municipio | id_municipio            | tipo_texto_generico | Coluna está como object.                         | Padronizar para string ou converter para tipo adequado. |
| meta_alfabetizacao_municipio | id_municipio            | validacao_chave     | Campo aparenta ser chave de relacionamento.      | Validar integridade referencial entre tabelas.          |
| meta_alfabetizacao_municipio | id_municipio_nome       | tipo_texto_generico | Coluna está como object.                         | Padronizar para string ou converter para tipo adequado. |
| meta_alfabetizacao_municipio | id_municipio_nome       | validacao_chave     | Campo aparenta ser chave de relacionamento.      | Validar integridade referencial entre tabelas.          |
| meta_alfabetizacao_municipio | rede                    | tipo_texto_generico | Coluna está como object.                         | Padronizar para string ou converter para tipo adequado. |
| meta_alfabetizacao_municipio | taxa_alfabetizacao      | valor_nulo          | Coluna possui 1.12% de valores nulos.            | Avaliar preenchimento, remoção ou manutenção como nulo. |
| meta_alfabetizacao_municipio | taxa_alfabetizacao      | validacao_intervalo | Campo percentual/proporcional deve ser validado. | Validar se os valores estão no intervalo esperado.      |
| meta_alfabetizacao_municipio | meta_alfabetizacao_2024 | valor_nulo          | Coluna possui 2.24% de valores nulos.            | Avaliar preenchimento, remoção ou manutenção como nulo. |
| meta_alfabetizacao_municipio | nivel_alfabetizacao     | valor_nulo          | Coluna possui 1.12% de valores nulos.            | Avaliar preenchimento, remoção ou manutenção como nulo. |
| meta_alfabetizacao_municipio | percentual_participacao | valor_nulo          | Coluna possui 1.12% de valores nulos.            | Avaliar preenchimento, remoção ou manutenção como nulo. |
| meta_alfabetizacao_municipio | percentual_participacao | validacao_intervalo | Campo percentual/proporcional deve ser validado. | Validar se os valores estão no intervalo esperado.      |
| meta_alfabetizacao_uf        | sigla_uf                | tipo_texto_generico | Coluna está como object.                         | Padronizar para string ou converter para tipo adequado. |
| meta_alfabetizacao_uf        | sigla_uf                | validacao_chave     | Campo aparenta ser chave de relacionamento.      | Validar integridade referencial entre tabelas.          |
| meta_alfabetizacao_uf        | sigla_uf_nome           | tipo_texto_generico | Coluna está como object.                         | Padronizar para string ou converter para tipo adequado. |
| meta_alfabetizacao_uf        | rede                    | tipo_texto_generico | Coluna está como object.                         | Padronizar para string ou converter para tipo adequado. |
| meta_alfabetizacao_uf        | taxa_alfabetizacao      | valor_nulo          | Coluna possui 4.94% de valores nulos.            | Avaliar preenchimento, remoção ou manutenção como nulo. |
| meta_alfabetizacao_uf        | taxa_alfabetizacao      | validacao_intervalo | Campo percentual/proporcional deve ser validado. | Validar se os valores estão no intervalo esperado.      |
| meta_alfabetizacao_uf        | meta_alfabetizacao_2024 | valor_nulo          | Coluna possui 11.11% de valores nulos.           | Avaliar preenchimento, remoção ou manutenção como nulo. |
| meta_alfabetizacao_uf        | meta_alfabetizacao_2025 | valor_nulo          | Coluna possui 3.7% de valores nulos.             | Avaliar preenchimento, remoção ou manutenção como nulo. |
| meta_alfabetizacao_uf        | meta_alfabetizacao_2026 | valor_nulo          | Coluna possui 2.47% de valores nulos.            | Avaliar preenchimento, remoção ou manutenção como nulo. |
| meta_alfabetizacao_uf        | meta_alfabetizacao_2027 | valor_nulo          | Coluna possui 2.47% de valores nulos.            | Avaliar preenchimento, remoção ou manutenção como nulo. |
| meta_alfabetizacao_uf        | meta_alfabetizacao_2028 | valor_nulo          | Coluna possui 2.47% de valores nulos.            | Avaliar preenchimento, remoção ou manutenção como nulo. |
| meta_alfabetizacao_uf        | meta_alfabetizacao_2029 | valor_nulo          | Coluna possui 2.47% de valores nulos.            | Avaliar preenchimento, remoção ou manutenção como nulo. |
| meta_alfabetizacao_uf        | meta_alfabetizacao_2030 | valor_nulo          | Coluna possui 2.47% de valores nulos.            | Avaliar preenchimento, remoção ou manutenção como nulo. |
| meta_alfabetizacao_uf        | percentual_participacao | valor_nulo          | Coluna possui 4.94% de valores nulos.            | Avaliar preenchimento, remoção ou manutenção como nulo. |
| meta_alfabetizacao_uf        | percentual_participacao | validacao_intervalo | Campo percentual/proporcional deve ser validado. | Validar se os valores estão no intervalo esperado.      |
| municipio                    | id_municipio            | tipo_texto_generico | Coluna está como object.                         | Padronizar para string ou converter para tipo adequado. |
| municipio                    | id_municipio            | validacao_chave     | Campo aparenta ser chave de relacionamento.      | Validar integridade referencial entre tabelas.          |
| municipio                    | id_municipio_nome       | tipo_texto_generico | Coluna está como object.                         | Padronizar para string ou converter para tipo adequado. |
| municipio                    | id_municipio_nome       | validacao_chave     | Campo aparenta ser chave de relacionamento.      | Validar integridade referencial entre tabelas.          |
| municipio                    | serie                   | tipo_texto_generico | Coluna está como object.                         | Padronizar para string ou converter para tipo adequado. |
| municipio                    | rede                    | tipo_texto_generico | Coluna está como object.                         | Padronizar para string ou converter para tipo adequado. |
| municipio                    | taxa_alfabetizacao      | validacao_intervalo | Campo percentual/proporcional deve ser validado. | Validar se os valores estão no intervalo esperado.      |
| municipio                    | proporcao_aluno_nivel_0 | valor_nulo          | Coluna possui 48.12% de valores nulos.           | Avaliar preenchimento, remoção ou manutenção como nulo. |
| municipio                    | proporcao_aluno_nivel_0 | validacao_intervalo | Campo percentual/proporcional deve ser validado. | Validar se os valores estão no intervalo esperado.      |
| municipio                    | proporcao_aluno_nivel_1 | valor_nulo          | Coluna possui 48.12% de valores nulos.           | Avaliar preenchimento, remoção ou manutenção como nulo. |
| municipio                    | proporcao_aluno_nivel_1 | validacao_intervalo | Campo percentual/proporcional deve ser validado. | Validar se os valores estão no intervalo esperado.      |
| municipio                    | proporcao_aluno_nivel_2 | valor_nulo          | Coluna possui 48.12% de valores nulos.           | Avaliar preenchimento, remoção ou manutenção como nulo. |
| municipio                    | proporcao_aluno_nivel_2 | validacao_intervalo | Campo percentual/proporcional deve ser validado. | Validar se os valores estão no intervalo esperado.      |
| municipio                    | proporcao_aluno_nivel_3 | valor_nulo          | Coluna possui 48.12% de valores nulos.           | Avaliar preenchimento, remoção ou manutenção como nulo. |
| municipio                    | proporcao_aluno_nivel_3 | validacao_intervalo | Campo percentual/proporcional deve ser validado. | Validar se os valores estão no intervalo esperado.      |
| municipio                    | proporcao_aluno_nivel_4 | valor_nulo          | Coluna possui 48.12% de valores nulos.           | Avaliar preenchimento, remoção ou manutenção como nulo. |
| municipio                    | proporcao_aluno_nivel_4 | validacao_intervalo | Campo percentual/proporcional deve ser validado. | Validar se os valores estão no intervalo esperado.      |
| municipio                    | proporcao_aluno_nivel_5 | valor_nulo          | Coluna possui 48.12% de valores nulos.           | Avaliar preenchimento, remoção ou manutenção como nulo. |
| municipio                    | proporcao_aluno_nivel_5 | validacao_intervalo | Campo percentual/proporcional deve ser validado. | Validar se os valores estão no intervalo esperado.      |
| municipio                    | proporcao_aluno_nivel_6 | valor_nulo          | Coluna possui 48.12% de valores nulos.           | Avaliar preenchimento, remoção ou manutenção como nulo. |
| municipio                    | proporcao_aluno_nivel_6 | validacao_intervalo | Campo percentual/proporcional deve ser validado. | Validar se os valores estão no intervalo esperado.      |
| municipio                    | proporcao_aluno_nivel_7 | valor_nulo          | Coluna possui 48.12% de valores nulos.           | Avaliar preenchimento, remoção ou manutenção como nulo. |
| municipio                    | proporcao_aluno_nivel_7 | validacao_intervalo | Campo percentual/proporcional deve ser validado. | Validar se os valores estão no intervalo esperado.      |
| municipio                    | proporcao_aluno_nivel_8 | valor_nulo          | Coluna possui 48.12% de valores nulos.           | Avaliar preenchimento, remoção ou manutenção como nulo. |
| municipio                    | proporcao_aluno_nivel_8 | validacao_intervalo | Campo percentual/proporcional deve ser validado. | Validar se os valores estão no intervalo esperado.      |
| uf                           | sigla_uf                | tipo_texto_generico | Coluna está como object.                         | Padronizar para string ou converter para tipo adequado. |
| uf                           | sigla_uf                | validacao_chave     | Campo aparenta ser chave de relacionamento.      | Validar integridade referencial entre tabelas.          |
| uf                           | sigla_uf_nome           | tipo_texto_generico | Coluna está como object.                         | Padronizar para string ou converter para tipo adequado. |
| uf                           | serie                   | tipo_texto_generico | Coluna está como object.                         | Padronizar para string ou converter para tipo adequado. |
| uf                           | rede                    | tipo_texto_generico | Coluna está como object.                         | Padronizar para string ou converter para tipo adequado. |
| uf                           | taxa_alfabetizacao      | validacao_intervalo | Campo percentual/proporcional deve ser validado. | Validar se os valores estão no intervalo esperado.      |
| uf                           | proporcao_aluno_nivel_0 | valor_nulo          | Coluna possui 48.28% de valores nulos.           | Avaliar preenchimento, remoção ou manutenção como nulo. |
| uf                           | proporcao_aluno_nivel_0 | validacao_intervalo | Campo percentual/proporcional deve ser validado. | Validar se os valores estão no intervalo esperado.      |
| uf                           | proporcao_aluno_nivel_1 | valor_nulo          | Coluna possui 48.28% de valores nulos.           | Avaliar preenchimento, remoção ou manutenção como nulo. |
| uf                           | proporcao_aluno_nivel_1 | validacao_intervalo | Campo percentual/proporcional deve ser validado. | Validar se os valores estão no intervalo esperado.      |
| uf                           | proporcao_aluno_nivel_2 | valor_nulo          | Coluna possui 48.28% de valores nulos.           | Avaliar preenchimento, remoção ou manutenção como nulo. |
| uf                           | proporcao_aluno_nivel_2 | validacao_intervalo | Campo percentual/proporcional deve ser validado. | Validar se os valores estão no intervalo esperado.      |
| uf                           | proporcao_aluno_nivel_3 | valor_nulo          | Coluna possui 48.28% de valores nulos.           | Avaliar preenchimento, remoção ou manutenção como nulo. |
| uf                           | proporcao_aluno_nivel_3 | validacao_intervalo | Campo percentual/proporcional deve ser validado. | Validar se os valores estão no intervalo esperado.      |
| uf                           | proporcao_aluno_nivel_4 | valor_nulo          | Coluna possui 48.28% de valores nulos.           | Avaliar preenchimento, remoção ou manutenção como nulo. |
| uf                           | proporcao_aluno_nivel_4 | validacao_intervalo | Campo percentual/proporcional deve ser validado. | Validar se os valores estão no intervalo esperado.      |
| uf                           | proporcao_aluno_nivel_5 | valor_nulo          | Coluna possui 48.28% de valores nulos.           | Avaliar preenchimento, remoção ou manutenção como nulo. |
| uf                           | proporcao_aluno_nivel_5 | validacao_intervalo | Campo percentual/proporcional deve ser validado. | Validar se os valores estão no intervalo esperado.      |
| uf                           | proporcao_aluno_nivel_6 | valor_nulo          | Coluna possui 48.28% de valores nulos.           | Avaliar preenchimento, remoção ou manutenção como nulo. |
| uf                           | proporcao_aluno_nivel_6 | validacao_intervalo | Campo percentual/proporcional deve ser validado. | Validar se os valores estão no intervalo esperado.      |
| uf                           | proporcao_aluno_nivel_7 | valor_nulo          | Coluna possui 48.28% de valores nulos.           | Avaliar preenchimento, remoção ou manutenção como nulo. |
| uf                           | proporcao_aluno_nivel_7 | validacao_intervalo | Campo percentual/proporcional deve ser validado. | Validar se os valores estão no intervalo esperado.      |
| uf                           | proporcao_aluno_nivel_8 | valor_nulo          | Coluna possui 48.28% de valores nulos.           | Avaliar preenchimento, remoção ou manutenção como nulo. |
| uf                           | proporcao_aluno_nivel_8 | validacao_intervalo | Campo percentual/proporcional deve ser validado. | Validar se os valores estão no intervalo esperado.      |