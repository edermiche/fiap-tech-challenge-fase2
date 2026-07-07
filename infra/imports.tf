# Recursos criados manualmente pelo console antes do Terraform.
# Os import blocks trazem cada um para o state na primeira execução
# de `terraform apply`; nas execuções seguintes são ignorados.

import {
  to = aws_s3_bucket.lake
  id = "fiap-alfabetizacao-lake-147997124244"
}

import {
  to = aws_s3_bucket_public_access_block.lake
  id = "fiap-alfabetizacao-lake-147997124244"
}

# O stream Kinesis criado pelo console foi destruído fora do período de
# demonstração (ver nota de FinOps em kinesis.tf); sem import, um apply
# completo o recria junto com o event source mapping do Lambda.

import {
  to = aws_iam_role.lambda_consumer
  id = "fiap-alfabetizacao-lambda-consumer"
}

import {
  to = aws_iam_role_policy.s3_put_bronze_streaming
  id = "fiap-alfabetizacao-lambda-consumer:s3-put-bronze-streaming"
}

import {
  to = aws_iam_role_policy_attachment.lambda_kinesis
  id = "fiap-alfabetizacao-lambda-consumer/arn:aws:iam::aws:policy/service-role/AWSLambdaKinesisExecutionRole"
}

import {
  to = aws_lambda_function.consumer
  id = "fiap-alfabetizacao-consumer"
}

# O event source mapping Kinesis -> Lambda criado pelo console foi
# removido manualmente depois; sem import, o Terraform o recria.
