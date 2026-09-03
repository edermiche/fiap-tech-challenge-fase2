# ADR-001 — Extração via BigQuery (multi-cloud) em vez de download direto do dataset

- **Status**: aceito
- **Data**: 2026-09-02
- **Decisores**: time do Tech Challenge Fase 2
- **Contexto relacionado**: [ADR-004 (ciclo de vida do S3)](ADR-004-ciclo-de-vida-armazenamento.md)

## Contexto

A [Base dos Dados](https://basedosdados.org/) publica o dataset
`br_inep_avaliacao_alfabetizacao` de duas formas: consulta via **BigQuery**
(SQL sobre as tabelas públicas) e **download direto** dos arquivos do dataset.

A pipeline roda em dois ambientes espelhados: local (`python main.py`) e AWS
(Glue Workflow em `sa-east-1`). A escolha da forma de extração define se a
arquitetura é single-cloud ou multi-cloud, e essa consequência não estava
documentada.

## Decisão

Manter a extração via **BigQuery**, com as sete consultas versionadas em
`queries/bronze/*.sql` e a trava de custo (`dry run` + `maximum_bytes_billed`)
descrita no README.

## Justificativa

1. **Filtragem e denormalização acontecem na origem.** As consultas não são
   `SELECT *`: `queries/bronze/alunos.sql` já resolve seis junções com as
   tabelas de dicionário (`serie`, `rede`, `presenca`, `alfabetizado`,
   `preenchimento_caderno`) e com o diretório de municípios. Baixando os
   arquivos, essas tabelas de apoio teriam que ser baixadas também e as
   junções refeitas localmente — a complexidade não desaparece, muda de lugar.
2. **Nenhum arquivo grande versionado nem hospedado.** A Bronze local tem
   ~141 MB *já filtrada*; o dataset completo é maior e teria que viver em
   algum lugar (repositório, S3 ou máquina do avaliador) antes do primeiro
   processamento.
3. **Custo de consulta é zero no nosso volume.** A extração completa processa
   ~260 MB, dentro do free tier de 1 TB/mês do BigQuery, e o
   `maximum_bytes_billed` impede que uma consulta mal escrita fure esse teto.
4. **Reprodutibilidade em SQL.** A extração é auditável linha a linha e
   reexecutável por quem tiver um projeto GCP, sem depender de um link de
   download continuar no ar.

## Consequências aceitas

Esta é a parte que a decisão cobra, e assumimos conscientemente:

- **Dependência de uma conta GCP com billing próprio.** Mesmo dentro do free
  tier, é preciso um projeto Google Cloud com faturamento habilitado. Na AWS
  isso vira uma service account guardada no Secrets Manager
  (`infra/secrets.tf`) — mais um segredo para rotacionar e mais um ponto de
  falha externo ao provedor principal.
- **Tráfego entre nuvens a cada carga.** O job Glue `bronze-ingestao` lê do
  BigQuery (GCP) e grava no S3 (`sa-east-1`): o resultado da consulta
  atravessa a internet pública toda vez que a Bronze é reprocessada. No nosso
  volume (~141 MB por execução completa) o egress do lado do Google fica na
  casa de centavos de dólar, mas é **recorrente e proporcional à frequência de
  execução**, não um custo único.
- **Duas superfícies de autenticação.** Credencial AWS (IAM) e credencial GCP
  (service account) na mesma pipeline.
- **Latência e falha de rede fora do nosso controle.** Uma indisponibilidade
  do BigQuery derruba a Bronze; o alerta SNS avisa, mas não há fallback.

## Alternativa considerada — download direto do arquivo

- **Ganhos**: arquitetura single-cloud, sem conta GCP, sem service account,
  sem egress recorrente entre nuvens. O custo de armazenamento passa a ser só
  o do S3, já coberto pelo ciclo de vida do [ADR-004](ADR-004-ciclo-de-vida-armazenamento.md).
- **Custos**: baixar o dataset inteiro (incluindo colunas e anos que não
  usamos) a cada nova safra; hospedar e versionar esse arquivo; reimplementar
  em pandas as junções com dicionários e diretórios que hoje são SQL na
  origem; perder a estimativa de volume por consulta que o `dry run` dá hoje.
- O projeto **já usa esse padrão onde ele cabe**: o FUNDEB entrou como CSV
  baixado uma vez (`downloads/fundeb_2024_2025_por_estado.csv`), porque é uma
  tabela pequena, anual e sem tabelas de apoio.

## Quando revisitar

A decisão deixa de valer a pena se qualquer um destes ocorrer:

- a execução passar de semanal para diária ou horária (o egress recorrente
  cresce na mesma proporção);
- o volume extraído passar da ordem de dezenas de GB por carga;
- houver exigência de arquitetura single-cloud (compliance, crédito AWS,
  ambiente corporativo sem conta GCP);
- a Base dos Dados passar a publicar os arquivos já denormalizados, o que
  eliminaria o principal ganho técnico do BigQuery.

Nesse caso, o ponto de troca é isolado: só `src/bronze/download_bigquery.py`
e as queries mudam. Bronze, Silver e Gold não sabem de onde o dado veio.
