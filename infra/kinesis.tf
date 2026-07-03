# Stream de eventos de avaliação de alunos — equivalente à fila local
# de micro-lotes (data/streaming/fila/).
#
# FinOps: 1 shard provisionado custa ~US$ 11/mês em sa-east-1; é o item
# mais caro do projeto. Fora de períodos de demonstração, vale destruir
# o stream (terraform destroy -target=aws_kinesis_stream.eventos).

resource "aws_kinesis_stream" "eventos" {
  name             = "${var.nome_projeto}-stream"
  shard_count      = 1
  retention_period = 24

  stream_mode_details {
    stream_mode = "PROVISIONED"
  }
}
