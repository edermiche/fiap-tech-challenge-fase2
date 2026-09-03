variable "regiao" {
  description = "Região AWS de todos os recursos."
  type        = string
  default     = "sa-east-1"
}

variable "nome_projeto" {
  description = "Prefixo dos nomes de recursos."
  type        = string
  default     = "fiap-alfabetizacao"
}

variable "bucket_lake" {
  description = "Nome do bucket S3 do data lake (bronze/silver/gold)."
  type        = string
  default     = "fiap-alfabetizacao-lake-147997124244"
}

variable "dias_bronze_standard_ia" {
  description = "Idade (dias) em que a partição Bronze vai para Standard-IA."
  type        = number
  default     = 30
}

variable "dias_bronze_glacier_ir" {
  description = "Idade (dias) em que a partição Bronze vai para Glacier Instant Retrieval."
  type        = number
  default     = 90
}

variable "dias_bronze_expiracao" {
  description = "Idade (dias) em que a partição Bronze é apagada."
  type        = number
  default     = 730
}

variable "dias_silver_standard_ia" {
  description = "Idade (dias) em que a partição Silver vai para Standard-IA."
  type        = number
  default     = 90
}

variable "pipeline_jobs" {
  description = <<-EOT
    Jobs Glue do pipeline, na ordem de execução do workflow.
    Cada nome precisa ter um script correspondente em src/glue/<nome>.py.
  EOT
  type        = list(string)
  default     = ["bronze_ingestao", "silver_transformacoes", "gold_analitica"]
}

variable "max_bytes_billed" {
  description = "Trava de custo por consulta BigQuery (bytes)."
  type        = string
  default     = "400000000"
}

variable "email_alertas" {
  description = "E-mail que recebe alertas de falha dos jobs (vazio = sem inscrição)."
  type        = string
  default     = ""
}

variable "agendamento_habilitado" {
  description = "Habilita o disparo agendado do pipeline via EventBridge Scheduler."
  type        = bool
  default     = false
}

variable "agendamento_cron" {
  description = "Expressão cron do EventBridge Scheduler (UTC)."
  type        = string
  default     = "cron(0 9 ? * MON *)"
}

variable "lambda_layer_pandas" {
  description = "ARN da layer gerenciada AWSSDKPandas (pandas + pyarrow) em sa-east-1."
  type        = string
  default     = "arn:aws:lambda:sa-east-1:336392948345:layer:AWSSDKPandas-Python312:20"
}
