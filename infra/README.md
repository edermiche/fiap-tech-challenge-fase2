# Infraestrutura AWS (Terraform)

Provisiona toda a arquitetura do pipeline na AWS — incluindo os recursos
que já existiam (bucket, Kinesis, Lambda consumer), importados para o
state via `import` blocks na primeira execução.

```text
EventBridge Scheduler ──▶ Glue Workflow (Python Shell + pandas)
                            └─ bronze_ingestao        (BigQuery → s3://…/bronze)
                               └─ silver_transformacoes  (bronze → s3://…/silver)
                                  └─ gold_analitica        (silver → s3://…/gold)

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

## Como as camadas Silver e Gold rodam na nuvem

Os jobs `silver_transformacoes` e `gold_analitica` não duplicam lógica:
o Terraform empacota `src/` em um zip no S3 (`glue/scripts/src_pipeline.zip`)
e cada job o baixa em tempo de execução e chama o mesmo
`processar_camada_silver()` / `processar_camada_gold()` da execução local.
Com a variável de ambiente `LAKE_S3_BUCKET` definida (feito pelos scripts
Glue), os leitores e gravadores do pipeline trocam `data/` pelo bucket,
mantendo o mesmo layout de partições.

Para plugar um job novo: criar `src/glue/<nome>.py`, acrescentar `<nome>`
à lista `pipeline_jobs` em `terraform.tfvars` e rodar `terraform apply` —
o upload do script, o job, o gatilho condicional no workflow e o alerta
de falha são gerados automaticamente a partir da lista.

## Ciclo de vida do S3

`aws_s3_bucket_lifecycle_configuration.lake` (em `s3.tf`) evita que a Bronze
cresça indefinidamente: cada execução acrescenta uma partição
`execution_date=<data>` e, sem política, nada expira.

| Prefixo | Política |
|---|---|
| `bronze/` | Standard-IA aos 30 dias → Glacier Instant Retrieval aos 90 → expira aos 730 |
| `silver/` | Standard-IA aos 90 dias, sem expiração |
| todo o bucket | Aborta upload multipart interrompido após 7 dias |

Prazos em `variables.tf` (`dias_bronze_standard_ia`, `dias_bronze_glacier_ir`,
`dias_bronze_expiracao`, `dias_silver_standard_ia`). Racional das escolhas —
inclusive por que Glacier **IR** e por que a Gold fica fora — em
[docs/adr/ADR-004](../docs/adr/ADR-004-ciclo-de-vida-armazenamento.md).

## Custos

| Recurso | Custo estimado |
|---|---|
| Kinesis (1 shard provisionado, 24/7) | ~US$ 11/mês — **destruir fora de demos** |
| Glue Python Shell (1 DPU) | ~US$ 0,01–0,04 por execução do pipeline |
| Secrets Manager | US$ 0,40/mês |
| S3 (~200 MB) + Lambda + EventBridge + SNS | centavos (com o ciclo de vida acima, não cresce com o histórico) |

O state fica local (`terraform.tfstate`, fora do git). Para desligar o
item mais caro sem derrubar o resto:
`terraform destroy -target=aws_lambda_event_source_mapping.kinesis -target=aws_kinesis_stream.eventos`
