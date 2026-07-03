# Alertas de falha do pipeline: EventBridge captura mudanças de estado
# dos jobs Glue (FAILED/TIMEOUT/STOPPED) e publica no SNS.

resource "aws_sns_topic" "alertas" {
  name = "${var.nome_projeto}-alertas"
}

resource "aws_sns_topic_subscription" "email" {
  count = var.email_alertas != "" ? 1 : 0

  topic_arn = aws_sns_topic.alertas.arn
  protocol  = "email"
  endpoint  = var.email_alertas
}

resource "aws_cloudwatch_event_rule" "glue_job_falha" {
  name        = "${var.nome_projeto}-glue-job-falha"
  description = "Falha em qualquer job Glue do pipeline."

  event_pattern = jsonencode({
    source        = ["aws.glue"]
    "detail-type" = ["Glue Job State Change"]
    detail = {
      state   = ["FAILED", "TIMEOUT", "STOPPED"]
      jobName = [for job in aws_glue_job.pipeline : job.name]
    }
  })
}

resource "aws_cloudwatch_event_target" "glue_falha_sns" {
  rule = aws_cloudwatch_event_rule.glue_job_falha.name
  arn  = aws_sns_topic.alertas.arn
}

resource "aws_sns_topic_policy" "permite_eventbridge" {
  arn = aws_sns_topic.alertas.arn

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect    = "Allow"
        Principal = { Service = "events.amazonaws.com" }
        Action    = "sns:Publish"
        Resource  = aws_sns_topic.alertas.arn
        Condition = {
          ArnEquals = { "aws:SourceArn" = aws_cloudwatch_event_rule.glue_job_falha.arn }
        }
      }
    ]
  })
}
