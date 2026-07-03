# Evidências da Execução em Nuvem (AWS)

Prints e registros da pipeline em execução na AWS (região `sa-east-1`),
coletados durante o teste de ponta a ponta descrito no README principal.

## Checklist de evidências

- [ ] `s3_camadas.png` — bucket do data lake com os prefixos bronze/, silver/ e gold/
- [ ] `s3_streaming_particoes.png` — arquivos parquet gravados pelo Lambda em bronze/alunos_streaming/ano=YYYY/
- [ ] `kinesis_metricas.png` — aba Monitoring do stream com os gráficos de IncomingRecords
- [ ] `lambda_invocacoes.png` — aba Monitor da função com as invocações do teste
- [ ] `cloudwatch_logs.png` — logs do Lambda mostrando os lotes processados

## Registro do teste de ponta a ponta (2026-07-02)

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
