# Valores do ambiente atual. Sem segredos aqui — a chave GCP vai
# direto pro Secrets Manager (ver README.md).

email_alertas = "lucas.alexsant2@gmail.com"

# Secret da service account GCP carregado em 2026-07-03; pipeline validado.
agendamento_habilitado = true

# Jobs Glue do pipeline, na ordem do workflow (bronze -> silver -> gold).
pipeline_jobs = ["bronze_ingestao", "silver_transformacoes", "gold_analitica"]

# A consulta de bolsa_familia_municipio agrega uma tabela de ~26 GB
# (novo_bolsa_familia, 2022-2024) — ~US$ 0,16 por varredura, dentro do
# free tier mensal de 1 TB do BigQuery. As demais consultas ficam bem
# abaixo; a trava continua protegendo contra varreduras descontroladas.
max_bytes_billed = "30000000000"
