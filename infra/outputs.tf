output "bucket_lake" {
  value = aws_s3_bucket.lake.bucket
}

output "kinesis_stream" {
  value = aws_kinesis_stream.eventos.name
}

output "lambda_consumer" {
  value = aws_lambda_function.consumer.function_name
}

output "glue_workflow" {
  value = aws_glue_workflow.pipeline.name
}

output "glue_jobs" {
  value = [for job in aws_glue_job.pipeline : job.name]
}

output "secret_gcp" {
  description = "Secret onde carregar a chave JSON da service account GCP."
  value       = aws_secretsmanager_secret.gcp_service_account.name
}

output "sns_alertas" {
  value = aws_sns_topic.alertas.arn
}
