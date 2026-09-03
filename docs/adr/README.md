# Decisões arquiteturais (ADRs)

Registro das decisões cujo trade-off não é óbvio no código: o que foi
decidido, por quê, e o que a decisão custa.

| ADR | Decisão | Consequência principal |
|---|---|---|
| [ADR-001](ADR-001-fonte-bigquery-vs-download.md) | Extrair via BigQuery em vez de baixar o dataset | Arquitetura multi-cloud: filtragem na origem, ao custo de dependência de conta GCP e tráfego entre nuvens a cada carga |
| [ADR-002](ADR-002-gate-de-qualidade.md) | Validação estrutural barra a execução; métricas persistidas em `gold.metricas_qualidade` | Safra corrompida não é publicada nem chega à Gold; qualidade passa a ter série histórica |
| [ADR-003](ADR-003-governanca-camada-gold.md) | Papel declarado por tabela Gold e consolidação das sobreposições | De 24 para 22 tabelas analíticas, com critério escrito para criar a próxima |
| [ADR-004](ADR-004-ciclo-de-vida-armazenamento.md) | Lifecycle Policy do S3 declarada no `s3.tf` | Crescimento da Bronze limitado por política, não por disciplina |
