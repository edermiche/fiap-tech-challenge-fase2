# Disparo agendado do pipeline via EventBridge Scheduler.
# Desabilitado por padrão (var.agendamento_habilitado) — habilitar
# depois que o secret da service account GCP estiver preenchido,
# senão o job bronze falha a cada disparo.

resource "aws_iam_role" "scheduler" {
  name = "${var.nome_projeto}-scheduler"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect    = "Allow"
        Principal = { Service = "scheduler.amazonaws.com" }
        Action    = "sts:AssumeRole"
      }
    ]
  })
}

resource "aws_iam_role_policy" "scheduler_start_workflow" {
  name = "start-glue-workflow"
  role = aws_iam_role.scheduler.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["glue:StartWorkflowRun"]
        Resource = aws_glue_workflow.pipeline.arn
      }
    ]
  })
}

resource "aws_scheduler_schedule" "pipeline" {
  name  = "${var.nome_projeto}-pipeline"
  state = var.agendamento_habilitado ? "ENABLED" : "DISABLED"

  schedule_expression = var.agendamento_cron

  flexible_time_window {
    mode = "OFF"
  }

  target {
    # Alvo universal: chamada direta à API StartWorkflowRun do Glue.
    arn      = "arn:aws:scheduler:::aws-sdk:glue:startWorkflowRun"
    role_arn = aws_iam_role.scheduler.arn

    input = jsonencode({
      Name = aws_glue_workflow.pipeline.name
    })
  }
}
