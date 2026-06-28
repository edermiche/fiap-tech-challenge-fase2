# FIAP Tech Challenge - Fase 2

## Pipeline Híbrido para Análise da Alfabetização no Brasil

Este projeto faz parte do Tech Challenge da Fase 2 e tem como objetivo construir uma pipeline de dados baseada na Arquitetura Medalhão, com camadas Bronze, Silver e Gold, para análise do Indicador Criança Alfabetizada.

A metodologia adotada será o CRISP-DM, adaptada para um contexto de Engenharia e Ciência de Dados.

## Estratégia de desenvolvimento

Para reduzir riscos de custo, a primeira versão do projeto será executada localmente em Jupyter Notebook.

Fluxo inicial:

1. Baixar os dados uma única vez da Base dos Dados / BigQuery.
2. Salvar os dados brutos na camada Bronze local em formato Parquet.
3. Gerar a camada Silver a partir da Bronze local.
4. Executar validações de qualidade.
5. Futuramente publicar as camadas finais na AWS S3.

## Estrutura do projeto

```text
fiap-tech-challenge-fase2/
├── data/
│   ├── bronze/
│   ├── silver/
│   └── gold/
├── docs/
├── notebooks/
│   ├── 01_download_bronze_bigquery.ipynb
│   ├── 02_silver_transformacoes.ipynb
│   └── 03_quality_checks.ipynb
├── queries/
│   └── uf_alfabetizacao.sql
├── src/
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## Camadas

### Bronze

Dados brutos extraídos da Base dos Dados, preservados sem transformações relevantes.

### Silver

Dados tratados, com padronização de colunas, tipos, valores ausentes e duplicidades.

### Gold

Camada analítica futura, preparada para dashboards, estatísticas e modelos de IA.

## Como iniciar

Crie o ambiente virtual:

```bash
python -m venv .venv
```

Ative no Windows PowerShell:

```bash
.venv\Scripts\Activate.ps1
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

Crie o arquivo `.env` com base no `.env.example`:

```env
GCP_PROJECT_ID=seu-project-id-google-cloud
```

Depois abra o notebook:

```text
notebooks/01_download_bronze_bigquery.ipynb
```

## Git

Primeiro commit sugerido:

```bash
git init
git add .
git commit -m "chore: estrutura inicial do projeto"
```
