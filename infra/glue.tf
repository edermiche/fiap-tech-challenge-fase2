# Jobs Glue (Python Shell) das camadas do pipeline, encadeados por um
# Glue Workflow: cada job só dispara quando o anterior conclui com
# sucesso. A lista var.pipeline_jobs define a ordem — para plugar as
# camadas Silver e Gold, basta acrescentar o nome do job à lista e
# criar o script correspondente em src/glue/.
#
# Python Shell (e não Spark): as transformações são pandas e o volume
# (~4 mi de linhas) cabe com folga em 1 DPU (16 GB), a fração de
# centavo por execução — mesma decisão de custo documentada no README.

locals {
  # Argumentos comuns a todos os jobs do pipeline.
  argumentos_comuns = {
    "library-set" = "analytics" # pandas, pyarrow, boto3, awswrangler
    "--S3_BUCKET" = aws_s3_bucket.lake.bucket
  }

  # Argumentos específicos por job. Jobs futuros (silver/gold) que só
  # leem e gravam no S3 não precisam de entrada aqui.
  argumentos_por_job = {
    bronze_ingestao = {
      "--additional-python-modules" = "google-cloud-bigquery,google-cloud-bigquery-storage,db-dtypes"
      "--GCP_SECRET_NAME"           = aws_secretsmanager_secret.gcp_service_account.name
      "--MAX_BYTES_BILLED"          = var.max_bytes_billed
      "--QUERIES_PREFIX"            = "glue/queries/bronze"
    }
  }

  # Pares (job -> próximo job) para os gatilhos condicionais do workflow.
  encadeamento = {
    for i, job in var.pipeline_jobs :
    job => var.pipeline_jobs[i + 1] if i < length(var.pipeline_jobs) - 1
  }
}

resource "aws_iam_role" "glue" {
  name = "${var.nome_projeto}-glue-pipeline"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect    = "Allow"
        Principal = { Service = "glue.amazonaws.com" }
        Action    = "sts:AssumeRole"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "glue_service" {
  role       = aws_iam_role.glue.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole"
}

resource "aws_iam_role_policy" "glue_lake_e_secret" {
  name = "lake-e-secret-gcp"
  role = aws_iam_role.glue.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["s3:ListBucket"]
        Resource = aws_s3_bucket.lake.arn
      },
      {
        Effect   = "Allow"
        Action   = ["s3:GetObject", "s3:PutObject", "s3:DeleteObject"]
        Resource = "${aws_s3_bucket.lake.arn}/*"
      },
      {
        Effect   = "Allow"
        Action   = ["secretsmanager:GetSecretValue"]
        Resource = aws_secretsmanager_secret.gcp_service_account.arn
      }
    ]
  })
}

resource "aws_glue_job" "pipeline" {
  for_each = toset(var.pipeline_jobs)

  name     = "${var.nome_projeto}-${replace(each.key, "_", "-")}"
  role_arn = aws_iam_role.glue.arn

  command {
    name            = "pythonshell"
    python_version  = "3.9"
    script_location = "s3://${aws_s3_bucket.lake.bucket}/glue/scripts/${each.key}.py"
  }

  max_capacity = 1.0
  max_retries  = 0
  timeout      = 60

  default_arguments = merge(
    local.argumentos_comuns,
    lookup(local.argumentos_por_job, each.key, {})
  )

  depends_on = [aws_s3_object.scripts_glue]
}

resource "aws_glue_workflow" "pipeline" {
  name        = "${var.nome_projeto}-pipeline"
  description = "Pipeline medalhão: ${join(" -> ", var.pipeline_jobs)}"
}

# Gatilho de partida: dispara o primeiro job quando o workflow é
# iniciado (manualmente, via console ou pelo EventBridge Scheduler).
resource "aws_glue_trigger" "inicio" {
  name          = "${var.nome_projeto}-inicio"
  type          = "ON_DEMAND"
  workflow_name = aws_glue_workflow.pipeline.name

  actions {
    job_name = aws_glue_job.pipeline[var.pipeline_jobs[0]].name
  }
}

# Encadeamento: job N+1 só dispara se o job N concluir com sucesso.
resource "aws_glue_trigger" "encadeamento" {
  for_each = local.encadeamento

  name              = "${var.nome_projeto}-apos-${replace(each.key, "_", "-")}"
  type              = "CONDITIONAL"
  workflow_name     = aws_glue_workflow.pipeline.name
  start_on_creation = true

  predicate {
    conditions {
      job_name = aws_glue_job.pipeline[each.key].name
      state    = "SUCCEEDED"
    }
  }

  actions {
    job_name = aws_glue_job.pipeline[each.value].name
  }
}
