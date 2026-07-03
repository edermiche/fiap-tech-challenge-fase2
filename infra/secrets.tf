# Service account do GCP usada pelo job de ingestão bronze para
# consultar o BigQuery. O Terraform cria apenas a "casca" do secret;
# o valor (JSON da chave) é carregado fora do state:
#
#   aws secretsmanager put-secret-value \
#     --secret-id fiap-alfabetizacao/gcp-service-account \
#     --secret-string file://caminho/para/chave.json

resource "aws_secretsmanager_secret" "gcp_service_account" {
  name        = "${var.nome_projeto}/gcp-service-account"
  description = "Chave JSON da service account GCP com leitura no BigQuery (Base dos Dados)."

  recovery_window_in_days = 0
}
