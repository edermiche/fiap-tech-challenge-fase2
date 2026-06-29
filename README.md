# Tech Challenge FIAP - Fase 2

Projeto de engenharia e análise de dados para acompanhar indicadores de alfabetização infantil no Brasil, usando dados públicos da Base dos Dados/INEP. A solução está organizada em camadas de dados, com foco inicial na ingestão e padronização da camada Bronze.

## Objetivo

Construir uma base analítica para responder perguntas sobre alfabetização no 2º ano do Ensino Fundamental, comparando resultados observados, metas oficiais e recortes por Brasil, UF, município, rede, escola e aluno.

O projeto segue uma abordagem inspirada no CRISP-DM:

- entendimento do negócio educacional;
- extração dos dados públicos;
- organização em camadas Bronze, Silver e Gold;
- análise de qualidade, chaves, relacionamentos e potenciais transformações;
- preparação de insumos para modelagem e análises futuras.

## Fontes de Dados

As consultas SQL em `queries/bronze/` extraem dados da Base dos Dados, principalmente do conjunto:

- `basedosdados.br_inep_avaliacao_alfabetizacao`

Entidades contempladas na camada Bronze:

- `alunos`
- `municipio`
- `uf`
- `meta_alfabetizacao_brasil`
- `meta_alfabetizacao_uf`
- `meta_alfabetizacao_municipio`

## Estrutura do Projeto

```text
.
├── data/
│   ├── bronze/              # dados brutos e arquivos processados da Bronze
│   ├── silver/              # espaço reservado para dados tratados
│   └── gold/                # espaço reservado para dados analíticos
├── docs/
│   ├── crisp_dm.md
│   ├── dicionario_dados_bronze.md
│   └── insumos_modelagem_bronze.md
├── notebooks/
│   ├── 01_download_bronze_bigquery.ipynb
│   ├── 01_entendimento_dados_bronze.ipynb
│   ├── 02_silver_transformacoes.ipynb
│   └── 03_quality_checks.ipynb
├── queries/
│   └── bronze/              # consultas SQL usadas na extração
├── src/
│   └── bronze/              # leitura, processamento e gravação da Bronze
├── main.py                  # ponto de entrada do pipeline Bronze
└── .env.example
```

## Pipeline Atual

O pipeline implementado em `src/bronze/` lê arquivos locais de cada entidade dentro de `data/bronze/<entidade>/`, consolida os dados em um único DataFrame e grava um arquivo Parquet processado.

Formatos aceitos na entrada:

- `.parquet`
- `.csv`
- `.xlsx`

Durante o processamento são adicionados metadados técnicos:

- `entidade_origem`
- `modo_ingestao`
- `data_ingestao_bronze`

Exemplo de saída:

```text
data/bronze/alunos/alunos_processado.parquet
```

## Como Executar

### 1. Criar e ativar ambiente virtual

```bash
python -m venv .venv
```

No Windows PowerShell:

```bash
.venv\Scripts\Activate.ps1
```

### 2. Instalar dependências mínimas

Ainda não há um arquivo `requirements.txt` no repositório. Para executar o pipeline atual, instale:

```bash
pip install pandas pyarrow openpyxl
```

Para usar os notebooks com BigQuery, também pode ser necessário instalar:

```bash
pip install jupyter google-cloud-bigquery pandas-gbq python-dotenv
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

Os dados locais não são versionados no Git.

### 5. Processar a camada Bronze

```bash
python main.py
```

O script processa todas as entidades configuradas em `src/bronze/config.py`.

## Documentação Analítica

Os principais artefatos de entendimento e qualidade estão em `docs/`:

- `crisp_dm.md`: visão do projeto segundo as etapas do CRISP-DM;
- `dicionario_dados_bronze.md`: perfil técnico inicial das tabelas Bronze;
- `insumos_modelagem_bronze.md`: chaves candidatas, relacionamentos e backlog para Silver.

## Próximos Passos

- Criar `requirements.txt` ou `pyproject.toml` para reproduzir o ambiente.
- Corrigir a codificação dos documentos existentes que estão com acentuação corrompida.
- Evoluir as transformações da camada Silver.
- Implementar validações automatizadas de qualidade.
- Definir métricas e tabelas finais da camada Gold.
- Automatizar a extração do BigQuery e a execução do pipeline.
