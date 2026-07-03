# Valores do ambiente atual. Sem segredos aqui — a chave GCP vai
# direto pro Secrets Manager (ver README.md).

email_alertas = "lucas.alexsant2@gmail.com"

# Secret da service account GCP carregado em 2026-07-03; pipeline validado.
agendamento_habilitado = true

# Plugar as próximas camadas quando os scripts existirem em src/glue/:
pipeline_jobs = ["bronze_ingestao"]
