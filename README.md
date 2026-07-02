# Tech Challenge FIAP — Fase 2

## Pipeline Híbrido para Análise da Alfabetização no Brasil

Pipeline de engenharia de dados em Arquitetura Medalhão (Bronze → Silver → Gold) com ingestão híbrida (batch + streaming), construído sobre dados públicos do INEP disponibilizados pela [Base dos Dados](https://basedosdados.org/), para acompanhar o **Indicador Criança Alfabetizada** no Brasil.

---

## 1. Contexto do Problema

A alfabetização na infância é um dos pilares do desenvolvimento educacional, social e econômico de um país. O **Compromisso Nacional Criança Alfabetizada** é a política pública que mobiliza União, estados, Distrito Federal e municípios com o objetivo de garantir que todas as crianças brasileiras estejam alfabetizadas até o final do 2º ano do Ensino Fundamental.

Para dar base objetiva a essa política, o INEP realizou em 2023 a **Pesquisa Alfabetiza Brasil**, que definiu o ponto de corte de **743 pontos na escala de proficiência do Saeb** como o nível a partir do qual uma criança é considerada alfabetizada. Desse parâmetro nasceu o **Indicador Criança Alfabetizada**: o percentual de estudantes que atingem esse patamar. A meta nacional é que, até **2030**, 100% das crianças estejam alfabetizadas ao final do 2º ano.

O desafio analítico: acompanhar esse indicador exige integrar fontes heterogêneas — metas nacionais, estaduais e municipais, dados territoriais e microdados de avaliação por aluno — com qualidade, escalabilidade e custo controlado. Este projeto simula o trabalho de um time de engenharia de dados de uma organização pública de análise educacional que constrói exatamente essa fundação.

### Perguntas de negócio que a pipeline responde

- Qual a taxa de alfabetização observada por Brasil, UF e município, e como ela se compara com as metas oficiais de cada ano?
- Quais UFs e municípios estão mais distantes das metas e deveriam ser priorizados por políticas públicas?
- Como o indicador evolui no tempo, em cada nível de agregação?

---

## 2. Arquitetura da Solução

### Visão geral

```mermaid
flowchart LR
    subgraph Fontes
        BD[("Base dos Dados<br/>(BigQuery)")]
    end

    subgraph Ingestão
        BATCH["Ingestão Batch<br/>(download_bigquery.py)"]
        PROD["Producer<br/>(eventos simulados)"]
        FILA["Stream<br/>(fila de micro-lotes)"]
        CONS["Consumer"]
    end

    subgraph "Arquitetura Medalhão"
        BRONZE["🥉 Bronze<br/>dados brutos<br/>parquet particionado"]
        SILVER["🥈 Silver<br/>dados tratados<br/>dims + fatos + flags de qualidade"]
        GOLD["🥇 Gold<br/>datasets analíticos<br/>metas vs resultados, rankings"]
    end

    subgraph Consumo
        DASH["Dashboards"]
        ML["Modelos de ML"]
        ANALISE["Análises estatísticas"]
    end

    BD -->|"batch (metas, territórios,<br/>agregados)"| BATCH --> BRONZE
    BD -.->|"origem dos eventos"| PROD
    PROD --> FILA --> CONS -->|"micro-lotes<br/>quase tempo real"| BRONZE
    BRONZE --> SILVER --> GOLD
    GOLD --> DASH & ML & ANALISE
```

### Fluxo de dados

1. **Extração batch**: `src/bronze/download_bigquery.py` consulta a Base dos Dados no BigQuery (com dry run de custo antes de cada execução) e grava as 6 entidades em parquet, particionadas por `execution_date`.
2. **Ingestão streaming (simulada)**: `src/streaming/producer.py` reemite medições de alunos como eventos em micro-lotes JSON; `src/streaming/consumer.py` consome a fila continuamente, adiciona metadados de ingestão e grava na Bronze particionado por ano.
3. **Consolidação Bronze**: `main.py` unifica os arquivos brutos de cada entidade com metadados técnicos (`entidade_origem`, `modo_ingestao`, `data_ingestao_bronze`).
4. **Transformação Silver**: `notebooks/02_silver_transformacoes.ipynb` limpa, padroniza tipos, remove duplicidades, normaliza chaves, cria flags de qualidade e modela dimensões e fatos.
5. **Camada Gold**: `notebooks/04_gold_analitica.ipynb` integra resultados e metas e materializa datasets prontos para consumo analítico.

### Mapeamento para nuvem (AWS)

A simulação local espelha, componente a componente, a arquitetura alvo em AWS:

| Componente local | Equivalente AWS | Papel |
|---|---|---|
| `data/` (parquet em camadas) | S3 (buckets bronze/silver/gold) | Data lake |
| `data/streaming/fila/` (micro-lotes JSON) | Kinesis Data Streams | Stream de eventos |
| `src/streaming/consumer.py` | Lambda (trigger no Kinesis) | Processamento de eventos |
| `src/bronze/download_bigquery.py` + `main.py` | Glue Job / Lambda agendado (EventBridge) | Ingestão batch |
| Notebooks Silver/Gold | Glue Job ou Databricks | Transformações |
| Prints/logs de execução | CloudWatch Logs + Metrics | Observabilidade |

Essa correspondência é deliberada: o código do consumer local é o corpo do handler do Lambda, e o producer muda apenas o destino (gravação em disco → `put_records` no Kinesis via boto3).

---

## 3. Ingestão Híbrida — por que cada fonte é batch ou streaming

| Fonte | Modo | Justificativa |
|---|---|---|
| Metas Brasil / UF / Município | **Batch** | Publicadas em ciclos oficiais anuais; não há ganho em processá-las continuamente |
| Município, UF (agregados) | **Batch** | Dados territoriais e agregados consolidados por ano de avaliação |
| Medições de alunos | **Streaming (simulado)** | Representa o cenário real de resultados de avaliação chegando incrementalmente de escolas/sistemas aplicadores. Não existe fonte pública de streaming para esses dados, então o producer simula esse comportamento em micro-lotes — o que basta para demonstrar o padrão arquitetural |

A decisão segue o princípio de usar streaming apenas onde a semântica do dado é de evento incremental — e não "porque foi pedido". O custo operacional de um stream só se justifica para a fonte que de fato se comportaria assim em produção.

---

## 4. Arquitetura Medalhão

### 🥉 Bronze — dados brutos

- 6 entidades: `alunos` (3,87 mi de linhas), `municipio`, `uf`, `meta_alfabetizacao_brasil`, `meta_alfabetizacao_uf`, `meta_alfabetizacao_municipio`
- Armazenamento sem transformações significativas, histórico preservado por partição `execution_date=YYYY-MM-DD`
- Eventos de streaming gravados em `alunos_streaming/ano=YYYY/`
- Metadados técnicos de rastreabilidade em todas as entidades

**Volume de dados**: o projeto trabalha com todo o histórico disponível do Indicador Criança Alfabetizada (avaliações de 2023 e 2024, metas projetadas até 2030). Indicador exige série histórica para comparação — descartar anos inviabilizaria a análise de evolução temporal.

### 🥈 Silver — dados tratados

12 tabelas modeladas em dimensões e fatos ([dicionário completo](docs/dicionario_dados_silver.md)):

- **Dimensões**: `dim_uf`, `dim_municipio`, `dim_escola`
- **Fatos de resultado**: `fato_resultado_brasil`, `fato_resultado_uf`, `fato_resultado_municipio`, `fato_resultado_meta_uf`
- **Fatos de metas** (colunas → linhas): `fato_meta_anual_brasil`, `fato_meta_anual_uf`
- **Distribuição por nível**: `fato_distribuicao_nivel_uf`, `fato_distribuicao_nivel_municipio`
- **Granularidade aluno**: `fato_aluno_alfabetizacao` (3,87 mi de linhas com flags de qualidade)

Transformações aplicadas: padronização de textos e códigos identificadores, conversão de tipos, remoção de duplicidades exatas, normalização de chaves, unpivot de metas anuais e níveis de proficiência, flags de validação (percentuais em [0,100], chaves preenchidas, valores não negativos) — registros inválidos são sinalizados, não descartados, preservando rastreabilidade.

### 🥇 Gold — camada analítica

7 datasets prontos para consumo ([dicionário completo](docs/dicionario_dados_gold.md)):

| Tabela | Pergunta que responde |
|---|---|
| `indicador_meta_brasil` / `_uf` / `_municipio` | Resultado observado vs. meta do mesmo ano, com status de atingimento |
| `evolucao_alfabetizacao` | Evolução temporal do indicador por nível de agregação |
| `ranking_uf_prioritaria` / `ranking_municipio_prioritario` | Priorização por distância à meta — insumo direto para política pública |
| `resumo_status_meta` | Consolidação de atingimento por ano e agregação |

---

## 5. Qualidade de Dados

Mecanismos implementados ao longo das camadas:

- **Duplicidade**: análise de chaves candidatas na Bronze ([insumos de modelagem](docs/insumos_modelagem_bronze.md)) e `drop_duplicates` sistemático na Silver
- **Valores ausentes**: perfil de nulos por coluna documentado nos dicionários; nulos legítimos (ex.: proficiência de alunos ausentes) preservados e sinalizados
- **Chaves de relacionamento**: validação de integridade referencial entre tabelas (cobertura de `id_municipio`, `sigla_uf`, `ano` entre origens — documentada nos insumos de modelagem)
- **Consistência**: flags de validação de intervalo em todos os campos percentuais; notebooks de quality checks (`03_quality_checks.ipynb`)

### Validadores visuais das camadas (`app/`)

Aplicações Flask para inspecionar os arquivos parquet gerados em cada camada pelo navegador — úteis para conferência rápida de qualidade sem abrir notebooks:

- `app/bronze_validator.py`, `app/silver_validator.py`, `app/gold_validator.py`: inspeção por camada
- `app/medallion_validator.py`: navegação entre as três camadas em uma única interface

Permitem listar tabelas, ver resumo de linhas/colunas, agrupar por eixo e métrica, gerar gráfico de barras, consultar a distribuição de `status_meta` e visualizar amostras.

```bash
python app/medallion_validator.py
# acesse http://127.0.0.1:5000
```

---

## 6. Decisões Arquiteturais (trade-offs)

**Batch vs. Streaming** — Kafka foi considerado e descartado: para o volume do projeto (milhares de eventos, não milhões/dia), operar um cluster Kafka é over-engineering. A simulação local com fila de micro-lotes demonstra o padrão e migra naturalmente para Kinesis Data Streams (gerenciado, 1 shard, custo próximo de zero no nosso volume), mantendo a semântica de producer/consumer.

**Data Lake vs. Data Warehouse** — optamos por data lake em parquet: os dados são públicos, o consumo é analítico e exploratório, e parquet colunar + particionamento entrega performance de leitura sem o custo fixo de um warehouse provisionado. Se o consumo evoluir para BI corporativo de alta concorrência, a Gold pode ser publicada em um warehouse (Athena/Redshift Spectrum leem o mesmo parquet no S3 sem migração).

**Custo vs. Performance** — o pipeline prioriza custo: processamento em micro-lotes em vez de streaming contínuo provisionado, transformações em pandas (suficiente para 3,9 mi de linhas; Spark seria justificável apenas acima de dezenas de milhões), armazenamento colunar comprimido. A performance de consulta é garantida pelo particionamento, não por computação cara.

---

## 7. Monitoramento e FinOps

### Monitoramento

- Estado atual: logs estruturados de execução em todas as etapas (entidade processada, volumetria, arquivos gerados), contagem de lotes/eventos no streaming, validações com relatório de aprovação/reprovação
- Arquitetura alvo (AWS): CloudWatch Logs para os jobs, métricas de Kinesis (records in/out, iterator age) para latência do stream, alarmes de falha de ingestão via CloudWatch Alarms + SNS

### FinOps

Decisões que reduzem custo operacional:

- **Parquet + particionamento** (`execution_date`, `ano`): leitura seletiva de partições reduz bytes escaneados — em Athena/BigQuery, custo é proporcional a bytes lidos
- **Dry run obrigatório antes da extração**: `download_bigquery.py` estima os bytes de cada consulta antes de executar e impõe `maximum_bytes_billed` como trava de custo (a extração completa processa ~260 MB, dentro do free tier de 1 TB/mês do BigQuery — custo real: R$ 0)
- **Cache de resultados**: re-execuções não repetem consultas (arquivos existentes são pulados)
- **Serverless por padrão na arquitetura alvo**: Lambda e Kinesis cobram por uso; não há cluster ocioso
- **Estimativa da arquitetura AWS no nosso volume**: S3 (~1 GB) + Kinesis (1 shard sob demanda) + Lambda (invocações esporádicas) ≈ **menos de US$ 5/mês**, dominado pelo custo fixo mínimo do stream

---

## 8. Aplicação em IA

A camada Gold foi desenhada para alimentar diretamente casos de uso de inteligência artificial:

- **Modelos de predição de alfabetização**: `fato_aluno_alfabetizacao` (Silver) fornece 3,87 mi de observações com proficiência, presença, rede e território — base para prever risco de não-alfabetização por município/escola. Enriquecida com fontes externas (Censo Escolar, indicadores socioeconômicos do IBGE), suporta modelos de regressão/classificação com features contextuais
- **Análise de desigualdade educacional**: as distribuições por nível de proficiência (`fato_distribuicao_nivel_*`) permitem medir dispersão intra-UF e clusters de vulnerabilidade educacional (ex.: k-means sobre distância à meta + nível socioeconômico)
- **Políticas públicas baseadas em dados**: os rankings de priorização da Gold são o insumo direto para alocação de recursos do Compromisso Nacional — a evolução temporal permite avaliar efeito de intervenções (diferença-em-diferenças entre municípios priorizados e não priorizados)

---

## 9. Tecnologias Utilizadas

| Tecnologia | Uso | Justificativa |
|---|---|---|
| Python 3.12 + pandas + pyarrow | Todo o pipeline | Stack padrão de dados; volume do projeto não justifica engine distribuída |
| Parquet | Armazenamento em todas as camadas | Colunar, comprimido, schema embutido; leitura seletiva de colunas/partições |
| BigQuery (Base dos Dados) | Fonte dos dados públicos | Dados INEP já estruturados e versionados; SQL padrão; free tier cobre o projeto |
| Jupyter Notebooks | Transformações Silver/Gold e análises | Documentação executável — código, resultado e decisão no mesmo artefato |
| Flask | Validadores visuais das camadas (`app/`) | Inspeção rápida dos parquets pelo navegador, sem depender de notebook |
| Git + GitHub (branches + PRs) | Versionamento e colaboração | Evolução rastreável do pipeline por feature branches e Pull Requests |
| AWS (S3, Kinesis, Lambda) | Arquitetura alvo em nuvem | Serverless, pay-per-use, aderente ao volume do projeto (ver seção FinOps) |

---

## 10. Estrutura do Repositório

```text
.
├── app/                           # validadores Flask das camadas (inspeção via navegador)
├── data/                          # data lake local (não versionado)
│   ├── bronze/                    #   brutos por entidade + partições execution_date
│   ├── silver/                    #   tabelas tratadas particionadas
│   ├── gold/                      #   datasets analíticos
│   └── streaming/                 #   fila de micro-lotes (simulação do stream)
├── docs/
│   ├── crisp_dm.md                # abordagem CRISP-DM do projeto
│   ├── dicionario_dados_bronze.md # perfil técnico das tabelas Bronze
│   ├── dicionario_dados_silver.md # dicionário das 12 tabelas Silver
│   ├── dicionario_dados_gold.md   # dicionário das 7 tabelas Gold
│   └── insumos_modelagem_bronze.md# chaves, relacionamentos e backlog
├── notebooks/
│   ├── 01_download_bronze_bigquery.ipynb
│   ├── 01_entendimento_dados_bronze.ipynb
│   ├── 02_silver_transformacoes.ipynb
│   ├── 03_quality_checks.ipynb
│   └── 04_gold_analitica.ipynb
├── queries/bronze/                # SQL de extração (Base dos Dados)
├── src/
│   ├── bronze/                    # ingestão batch (leitura, gravação, download BigQuery)
│   └── streaming/                 # producer e consumer da ingestão streaming
├── main.py                        # consolidação da camada Bronze
├── requirements.txt
└── .env.example
```

---

## 11. Como Executar

### Pré-requisitos

- Python 3.12+
- Conta Google Cloud com um projeto criado (só para a extração; free tier suficiente)

### Setup

```bash
# 1. Ambiente virtual
python -m venv .venv
.venv\Scripts\Activate.ps1        # Windows | source .venv/bin/activate (Linux/Mac)

# 2. Dependências
pip install -r requirements.txt

# 3. Variáveis de ambiente
copy .env.example .env            # e preencha GCP_PROJECT_ID
```

### Pipeline batch

```bash
# 4. Extração da Base dos Dados (abre o navegador para login Google)
python -m src.bronze.download_bigquery              # use --somente-dry-run para só estimar custo

# 5. Consolidação Bronze
python main.py

# 6. Silver e Gold: executar os notebooks 02 e 04 em ordem
jupyter notebook
```

### Pipeline streaming (dois terminais)

```bash
# Terminal 1 — consumer (inicie primeiro)
python -m src.streaming.consumer

# Terminal 2 — producer
python -m src.streaming.producer --total-eventos 1000 --tamanho-lote 100
```

O consumer encerra sozinho após ciclos consecutivos de fila vazia (configurável via `--max-ciclos-vazios`).

---

## 12. Metodologia

O projeto segue a abordagem **CRISP-DM** (entendimento do negócio → entendimento dos dados → preparação → modelagem → avaliação → implantação), documentada em [docs/crisp_dm.md](docs/crisp_dm.md). Os artefatos de entendimento e qualidade de cada etapa estão em `docs/`.

---

## 13. Próximos Passos

- [ ] Provisionamento AWS via IaC (S3 + Kinesis Data Streams + Lambda) com evidências de execução
- [ ] Atualização do notebook de quality checks para a estrutura atual da Silver
- [ ] Monitoramento com CloudWatch (logs, métricas e alarmes)
- [ ] Enriquecimento com fontes externas (Censo Escolar, IBGE) para os casos de uso de IA
- [ ] Vídeo executivo (até 5 min)
