# Evidências da Execução do Pipeline

Prints e registros da pipeline em execução local e na AWS (região `sa-east-1`),
coletados durante os testes de ponta a ponta descritos no README principal.

## Checklist de evidências (prints)

Teste de 2026-07-07 — Glue Workflow (bronze → silver → gold) e recursos do streaming:

- [x] `glue_workflow.png` — grafo do workflow `fiap-alfabetizacao-pipeline` com os 3 jobs SUCCEEDED
- [x] `glue_jobs.png` — histórico de execuções dos jobs com duração
- [x] `cloudwatch_jobs_output.png` — log group dos jobs Glue, incluindo a união híbrida no silver (`Alunos híbrido: 3867999 batch + 2000 streaming`)
- [x] `s3_bronze.png` — camada bronze no lake, incluindo `alunos_streaming/ano=YYYY/` gravado pelo Lambda
- [x] `s3_silver.png` — partições `execution_date=` na camada silver
- [x] `s3_gold.png` — partições `execution_date=` na camada gold
- [x] `lambda_consumer.png` — função `fiap-alfabetizacao-consumer` (consumer do streaming, invocada no teste de 2026-07-02)
- [x] `notificacao_error_sns.png` — e-mail de alerta recebido no teste de falha controlada (2026-07-07)

> As métricas do Kinesis não têm mais print disponível: o stream foi destruído por FinOps
> após o teste de 2026-07-02 (registro textual abaixo). O funcionamento fica evidenciado
> pelo log do CloudWatch daquele teste e pelos parquet em `bronze/alunos_streaming/`.

Links do console para os prints (região `sa-east-1`):

- Glue Workflow: <https://sa-east-1.console.aws.amazon.com/glue/home?region=sa-east-1#/v2/etl-configuration/workflows/view/fiap-alfabetizacao-pipeline>
- Glue Jobs: <https://sa-east-1.console.aws.amazon.com/glue/home?region=sa-east-1#/v2/etl-configuration/jobs>
- CloudWatch (log group dos jobs): <https://sa-east-1.console.aws.amazon.com/cloudwatch/home?region=sa-east-1#logsV2:log-groups/log-group/$252Faws-glue$252Fpython-jobs$252Foutput>
- S3 silver: <https://s3.console.aws.amazon.com/s3/buckets/fiap-alfabetizacao-lake-147997124244?region=sa-east-1&prefix=silver/>
- S3 gold: <https://s3.console.aws.amazon.com/s3/buckets/fiap-alfabetizacao-lake-147997124244?region=sa-east-1&prefix=gold/>
- Lambda consumer: <https://sa-east-1.console.aws.amazon.com/lambda/home?region=sa-east-1#/functions/fiap-alfabetizacao-consumer?tab=monitoring>

## Logs de execução ([logs/](logs/))

| Arquivo | Conteúdo |
|---|---|
| `producer_local.log` | Producer local: 500 eventos em 5 micro-lotes para a fila |
| `consumer_local.log` | Consumer local: 5 lotes consumidos e gravados na bronze `alunos_streaming/` |
| `pipeline_local.log` | `python main.py` completo (bronze → silver → gold) com a união híbrida |
| `glue_bronze_cloudwatch.log` | Job Glue `bronze-ingestao` (BigQuery → S3 com dry run de custo) |
| `glue_silver_cloudwatch.log` | Job Glue `silver-transformacoes` lendo batch + streaming do S3 |
| `glue_gold_cloudwatch.log` | Job Glue `gold-analitica` materializando os 23 datasets no S3 |
| `glue_workflow_run.json` | Resumo da execução do workflow (status, horários e duração por job) |
| `gate_qualidade_local.log` | Gate de qualidade e histórico `gold.metricas_qualidade`: execução aprovada, cobertura territorial, comparação com a safra anterior, demonstração do bloqueio e `pytest tests/` |

## Registro do gate de qualidade — execução local (2026-09-01 e 2026-09-02)

Log completo em [`logs/gate_qualidade_local.log`](logs/gate_qualidade_local.log).

Duas execuções completas (bronze → silver → gold), para exercitar as regras
comparativas com histórico real:

| Execução | Métricas gravadas |
|---|---|
| `execution_date=2026-09-01` | 177 (153 Silver + 24 Gold) |
| `execution_date=2026-09-02` | 187 (160 Silver + 27 Gold) |

- Ambas aprovadas no gate: 5 alertas, nenhuma violação bloqueante
- Histórico funcionando: a segunda execução leu as métricas da primeira e
  registrou `aumento_ausencia_safra_anterior` (7 tabelas de fato) e
  `queda_cobertura_safra_anterior` (3 recortes territoriais) — todos sem piora
- Cobertura territorial registrada: `gold.indicador_meta_uf` publica 24 das 27
  UFs em 2024 (AC e DF sem meta 2024 na fonte, RR sem resultado até 2024) — a
  lacuna virou alerta com número, em vez de sumir em silêncio
- Bloqueio demonstrado no cenário do enunciado — extração com 100% dos percentuais
  fora de `[0,100]`:

```text
Gate de qualidade reprovado (1 violações bloqueantes). A camada não foi publicada
e o pipeline foi interrompido.
  - silver.fato_resultado_uf percentual_fora_intervalo(taxa_alfabetizacao):
    100.00% (145/145 registros) > limite 5.00%
```

- `pytest tests/`: 12 testes passando (barra o percentual inválido, não barra a
  deduplicação de dimensão, persiste e compara o histórico, mede cobertura e
  detecta queda de cobertura entre safras)

## Registro do teste de ponta a ponta — streaming AWS (2026-07-02)

- 500 eventos reais de alunos enviados via `python -m src.streaming.producer --destino kinesis --total-eventos 500`
- Kinesis `fiap-alfabetizacao-stream`: 5 micro-lotes de 100 eventos recebidos
- Lambda `fiap-alfabetizacao-consumer`: 5 invocações, 100% de sucesso
- S3: 10 arquivos parquet gravados (partições `ano=2023` e `ano=2024`)
- Log de exemplo (CloudWatch):

```text
2026-07-02T23:15:14 Lote processado: 100 eventos, 2 arquivo(s) gravado(s):
['bronze/alunos_streaming/ano=2023/eventos_20260702_231513_571657.parquet',
 'bronze/alunos_streaming/ano=2024/eventos_20260702_231513_571657.parquet']
```

> Após o teste, o stream Kinesis foi destruído (`terraform destroy -target=aws_kinesis_stream.eventos`)
> por FinOps — é o recurso mais caro do projeto (~US$ 11/mês) e só precisa existir
> durante demonstrações. As evidências acima registram o funcionamento.

## Registro do teste de ponta a ponta — pipeline híbrido (2026-07-07)

### Local (simulação completa sem AWS)

- Producer publicou 500 eventos em 5 micro-lotes na fila local (`producer_local.log`)
- Consumer consumiu os 5 lotes e gravou na bronze `alunos_streaming/ano=YYYY/` (`consumer_local.log`)
- `python main.py` executou bronze → silver → gold com a união híbrida (`pipeline_local.log`):

```text
Lendo bronze streaming: data\bronze\alunos_streaming
Alunos híbrido: 3867999 batch + 2000 streaming
```

### AWS (Glue Workflow `fiap-alfabetizacao-pipeline`)

Execução `wr_bd176603...aae6` — **COMPLETED**, 3/3 ações com sucesso (`glue_workflow_run.json`):

| Job | Estado | Duração |
|---|---|---|
| `fiap-alfabetizacao-bronze-ingestao` | SUCCEEDED | 42 s |
| `fiap-alfabetizacao-silver-transformacoes` | SUCCEEDED | 135 s |
| `fiap-alfabetizacao-gold-analitica` | SUCCEEDED | 106 s |

- Job silver leu as 7 entidades batch **e** os eventos de `bronze/alunos_streaming/` do S3,
  unindo as duas origens (`Alunos híbrido: 3867999 batch + 2000 streaming` — replays
  deduplicados pela chave natural, sem duplicar aluno)
- 76 objetos gravados no lake com `execution_date=2026-07-07` (silver + gold)
- Kinesis permaneceu desligado: o streaming em nuvem foi evidenciado no teste de 2026-07-02;
  os eventos que ele gravou na bronze S3 foram consumidos agora pela silver — fechando o
  ciclo híbrido também na nuvem

### Teste do alerta de falha (EventBridge → SNS → e-mail)

Falha controlada para exercitar o monitoramento, executada fora do workflow
(job avulso com `--SRC_ZIP_KEY` apontando para um zip inexistente — não toca no lake):

- Job `fiap-alfabetizacao-silver-transformacoes`, run `jr_dfe62dc9...da261f`:
  **FAILED** em 17 s com `NoSuchKey: The specified key does not exist`
- Regra EventBridge `fiap-alfabetizacao-glue-job-falha` capturou a mudança de estado
- SNS `fiap-alfabetizacao-alertas`: `NumberOfNotificationsDelivered = 1` — e-mail de
  alerta entregue à assinatura confirmada (`lucas.alexsant2@gmail.com`)

> A assinatura de e-mail original havia expirado sem confirmação (o SNS descarta
> assinaturas pendentes após 3 dias); foi recriada e confirmada em 2026-07-07 antes do teste.
