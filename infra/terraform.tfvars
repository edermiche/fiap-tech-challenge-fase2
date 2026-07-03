# Valores do ambiente atual. Sem segredos aqui — a chave GCP vai
# direto pro Secrets Manager (ver README.md).

email_alertas = "marceloaggio10@gmail.com"

# Habilitar somente depois de carregar o secret da service account GCP:
agendamento_habilitado = false

# Plugar as próximas camadas quando os scripts existirem em src/glue/:
pipeline_jobs = ["bronze_ingestao"]
