# Tech Challenge FIAP - Fase 2

Projeto de engenharia e análise de dados para acompanhar indicadores de alfabetização infantil no Brasil a partir de dados públicos da Base dos Dados/INEP. A solução está organizada em arquitetura medalhão, com camadas Bronze, Silver e Gold, além de aplicações Flask simples para validar os dados gerados em cada camada.

## Objetivo

Construir uma base analítica para responder perguntas sobre alfabetização no 2º ano do Ensino Fundamental, comparando resultados observados, metas oficiais e recortes por Brasil, UF, município, rede, escola e aluno.

O projeto segue uma abordagem inspirada no CRISP-DM:

- entendimento do negócio educacional;
- extração dos dados públicos;
- organização em camadas Bronze, Silver e Gold;
- análise de qualidade, chaves e relacionamentos;
- criação de indicadores finais para avaliação das metas de alfabetização.

## Fontes de Dados

As consultas SQL em `queries/bronze/` extraem dados da Base dos Dados, principalmente do conjunto:

- `basedosdados.br_inep_avaliacao_alfabetizacao`

Entidades da camada Bronze:

- `alunos`
- `municipio`
- `uf`
- `meta_alfabetizacao_brasil`
- `meta_alfabetizacao_uf`
- `meta_alfabetizacao_municipio`

## Estrutura do Projeto

```text
.
+-- app/
|   +-- bronze_validator.py
|   +-- gold_validator.py
|   +-- medallion_validator.py
|   +-- silver_validator.py
+-- data/
|   +-- bronze/
|   +-- silver/
|   +-- gold/
+-- docs/
|   +-- crisp_dm.md
|   +-- dicionario_dados_bronze.md
|   +-- dicionario_dados_silver.md
|   +-- dicionario_dados_gold.md
|   +-- insumos_modelagem_bronze.md
+-- notebooks/
|   +-- 01_download_bronze_bigquery.ipynb
|   +-- 01_entendimento_dados_bronze.ipynb
|   +-- 02_silver_transformacoes.ipynb
|   +-- 03_quality_checks.ipynb
|   +-- 04_gold_analitica.ipynb
+-- queries/
|   +-- bronze/
+-- src/
|   +-- bronze/
+-- main.py
+-- requirements.txt
+-- .env.example
```

Os arquivos de dados locais não são versionados no Git. As pastas `data/bronze`, `data/silver` e `data/gold` mantêm apenas arquivos `.gitkeep`.

## Camadas de Dados

### Bronze

A camada Bronze recebe os dados brutos extraídos do BigQuery/Base dos Dados. O pipeline em `src/bronze/` lê arquivos locais em `data/bronze/<entidade>/`, consolida cada entidade e grava um Parquet processado.

Formatos aceitos na entrada:

- `.parquet`
- `.csv`
- `.xlsx`

Metadados adicionados na Bronze:

- `entidade_origem`
- `modo_ingestao`
- `data_ingestao_bronze`

### Silver

A camada Silver, construída nos notebooks, organiza dados tratados e padronizados para consumo analítico. A documentação atual identifica 12 tabelas Silver, incluindo dimensões e fatos:

- `silver.dim_escola`
- `silver.dim_municipio`
- `silver.dim_uf`
- `silver.fato_aluno_alfabetizacao`
- `silver.fato_distribuicao_nivel_municipio`
- `silver.fato_distribuicao_nivel_uf`
- `silver.fato_meta_anual_brasil`
- `silver.fato_meta_anual_uf`
- `silver.fato_resultado_brasil`
- `silver.fato_resultado_meta_uf`
- `silver.fato_resultado_municipio`
- `silver.fato_resultado_uf`

Veja `docs/dicionario_dados_silver.md` para o dicionário completo.

### Gold

A camada Gold contém tabelas analíticas finais derivadas da Silver, focadas na comparação entre taxa observada e meta de alfabetização.

Tabelas Gold documentadas:

- `gold.indicador_meta_brasil`
- `gold.indicador_meta_uf`
- `gold.ranking_uf_prioritaria`

Veja `docs/dicionario_dados_gold.md` para detalhes das colunas, tipos, nulos e exemplos.

## Como Executar

### 1. Criar e ativar o ambiente virtual

```bash
python -m venv .venv
```

No Windows PowerShell:

```bash
.venv\Scripts\Activate.ps1
```

### 2. Instalar dependências

O projeto possui `requirements.txt` com as dependências usadas nos notebooks, pipeline e aplicações Flask.

```bash
pip install -r requirements.txt
```

### 3. Configurar variáveis de ambiente

Copie o arquivo de exemplo:

```bash
copy .env.example .env
```

Preencha o projeto Google Cloud:

```env
GCP_PROJECT_ID=seu-project-id-google-cloud
```

### 4. Baixar ou disponibilizar os dados brutos

Use o notebook `notebooks/01_download_bronze_bigquery.ipynb` ou as consultas em `queries/bronze/` para obter os dados.

Depois, salve os arquivos nas pastas esperadas pelo pipeline:

```text
data/bronze/alunos/
data/bronze/municipio/
data/bronze/uf/
data/bronze/meta_alfabetizacao_brasil/
data/bronze/meta_alfabetizacao_uf/
data/bronze/meta_alfabetizacao_municipio/
```

### 5. Processar a camada Bronze

```bash
python main.py
```

O script processa todas as entidades configuradas em `src/bronze/config.py`.

### 6. Gerar Silver, validações e Gold

Execute os notebooks na sequência:

```text
notebooks/02_silver_transformacoes.ipynb
notebooks/03_quality_checks.ipynb
notebooks/04_gold_analitica.ipynb
```

## Validadores das Camadas

O diretório `app/` disponibiliza aplicações Flask para inspecionar os arquivos Parquet gerados nas camadas do projeto.

Validadores disponíveis:

- `app/bronze_validator.py`: inspeciona tabelas da camada Bronze;
- `app/silver_validator.py`: inspeciona tabelas da camada Silver;
- `app/gold_validator.py`: inspeciona tabelas da camada Gold;
- `app/medallion_validator.py`: permite navegar entre Bronze, Silver e Gold em uma única interface.

As aplicações permitem:

- listar tabelas disponíveis;
- selecionar uma tabela;
- escolher eixo de agrupamento e métrica numérica;
- visualizar resumo de linhas e colunas;
- gerar gráfico simples de barras;
- consultar distribuição de `status_meta`, quando existir;
- visualizar amostra dos dados.

Para executar o validador geral:

```bash
python app/medallion_validator.py
```

Acesse no navegador:

```text
http://127.0.0.1:5000
```

## Documentação

Os principais artefatos de documentação estão em `docs/`:

- `crisp_dm.md`: visão do projeto segundo as etapas do CRISP-DM;
- `dicionario_dados_bronze.md`: perfil técnico inicial das tabelas Bronze;
- `insumos_modelagem_bronze.md`: chaves candidatas, relacionamentos e backlog inicial;
- `dicionario_dados_silver.md`: dicionário das tabelas tratadas da Silver;
- `dicionario_dados_gold.md`: dicionário das tabelas analíticas finais da Gold.

## Estado Atual

- Bronze: pipeline Python implementado em `src/bronze/`.
- Silver: transformações e dicionário documentados.
- Gold: três tabelas analíticas documentadas.
- Validação: aplicações Flask criadas para leitura e inspeção dos Parquets Bronze, Silver e Gold.
- Ambiente: dependências registradas em `requirements.txt`.

## Próximos Passos

- Automatizar a execução sequencial Bronze, Silver e Gold fora dos notebooks.
- Corrigir a codificação dos documentos antigos que ainda aparecem com acentuação corrompida em alguns ambientes.
- Adicionar testes automatizados para regras de qualidade.
- Versionar contratos de schema para as tabelas Silver e Gold.
- Preparar publicação futura dos dados finais em ambiente cloud.
