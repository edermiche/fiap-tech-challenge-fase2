# Infraestrutura AWS (Terraform)

Provisiona toda a arquitetura do pipeline na AWS — incluindo os recursos
que já existiam (bucket, Kinesis, Lambda consumer), importados para o
state via `import` blocks na primeira execução.

```text
EventBridge Scheduler ──▶ Glue Workflow (Python Shell + pandas)
                            └─ bronze_ingestao (BigQuery → s3://…/bronze)
                               └─ [silver_transformacoes]   ← plugar depois
                                  └─ [gold_analitica]       ← plugar depois

producer local ──▶ Kinesis ──▶ Lambda consumer ──▶ s3://…/bronze/alunos_streaming
Falha de job Glue ──▶ EventBridge rule ──▶ SNS (e-mail)
```

## Como aplicar

```bash
cd infra
terraform init
terraform plan    # primeira execução mostra 8 imports + criações
terraform apply
```

## Carregar a service account GCP (pré-requisito do job bronze)

O job `bronze_ingestao` consulta o BigQuery com uma service account
(roles `BigQuery Job User` e `BigQuery Read Session User`). A chave
JSON fica no Secrets Manager, nunca no repositório:

```bash
aws secretsmanager put-secret-value \
  --secret-id fiap-alfabetizacao/gcp-service-account \
  --secret-string file://caminho/para/chave.json
```

## Rodar o pipeline

```bash
# manual (demo)
aws glue start-workflow-run --name fiap-alfabetizacao-pipeline

# agendado: setar agendamento_habilitado = true (terraform.tfvars) e aplicar
```

## Como plugar as camadas Silver e Gold

Quando as transformações locais estiverem prontas:

1. Criar `src/glue/silver_transformacoes.py` (e depois `gold_analitica.py`)
   lendo/gravando no S3 — usar `src/glue/bronze_ingestao.py` como modelo
   de leitura de argumentos e escrita em parquet;
2. Acrescentar o nome à lista em `terraform.tfvars`:
   `pipeline_jobs = ["bronze_ingestao", "silver_transformacoes", "gold_analitica"]`;
3. `terraform apply`.

O upload do script, o job, o gatilho condicional no workflow e o alerta
de falha são gerados automaticamente a partir da lista.

## Custos

| Recurso | Custo estimado |
|---|---|
| Kinesis (1 shard provisionado, 24/7) | ~US$ 11/mês — **destruir fora de demos** |
| Glue Python Shell (1 DPU) | ~US$ 0,01–0,04 por execução do pipeline |
| Secrets Manager | US$ 0,40/mês |
| S3 (~200 MB) + Lambda + EventBridge + SNS | centavos |

O state fica local (`terraform.tfstate`, fora do git). Para desligar o
item mais caro sem derrubar o resto:
`terraform destroy -target=aws_lambda_event_source_mapping.kinesis -target=aws_kinesis_stream.eventos`
