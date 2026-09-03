# Data lake em camadas (bronze/silver/gold) — equivalente ao data/ local.

resource "aws_s3_bucket" "lake" {
  bucket = var.bucket_lake
}

# Ciclo de vida do lake — o único vazamento de custo que sobrava.
#
# A Bronze guarda todo o histórico particionado por execution_date e cada
# reprocessamento acrescenta uma partição nova, sem nada expirar. Hoje são
# ~150 MB e ninguém sente; com o Scheduler semanal ligado, a conta cresce
# sozinha. As regras abaixo esfriam e expiram esse histórico sem exigir
# nenhuma mudança no pipeline: a chave S3 não muda, só a classe de
# armazenamento.
#
# Por que GLACIER_IR e não GLACIER/DEEP_ARCHIVE: Instant Retrieval mantém
# leitura em milissegundos, então um reprocessamento a partir da Bronze
# antiga continua funcionando sem job de restore — a economia é menor,
# mas não quebra a reprodutibilidade, que é o motivo de guardar a Bronze.
#
# Silver e Gold esfriam mais tarde e não expiram: a execução corrente é o
# que os dashboards leem. Objeto menor que 128 KB não é transicionado
# (a AWS cobra o mínimo de 128 KB no IA), então as dimensões pequenas
# ficam em Standard mesmo — o ganho está nas partições grandes de fato.
resource "aws_s3_bucket_lifecycle_configuration" "lake" {
  bucket = aws_s3_bucket.lake.id

  rule {
    id     = "bronze-historico"
    status = "Enabled"

    filter {
      prefix = "bronze/"
    }

    transition {
      days          = var.dias_bronze_standard_ia
      storage_class = "STANDARD_IA"
    }

    transition {
      days          = var.dias_bronze_glacier_ir
      storage_class = "GLACIER_IR"
    }

    expiration {
      days = var.dias_bronze_expiracao
    }
  }

  rule {
    id     = "silver-execucoes-antigas"
    status = "Enabled"

    filter {
      prefix = "silver/"
    }

    transition {
      days          = var.dias_silver_standard_ia
      storage_class = "STANDARD_IA"
    }
  }

  # Upload multipart interrompido não aparece no console e continua sendo
  # cobrado até ser abortado.
  rule {
    id     = "abortar-uploads-incompletos"
    status = "Enabled"

    filter {}

    abort_incomplete_multipart_upload {
      days_after_initiation = 7
    }
  }
}

resource "aws_s3_bucket_public_access_block" "lake" {
  bucket = aws_s3_bucket.lake.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Scripts dos jobs Glue — o Glue lê o script direto do S3.
resource "aws_s3_object" "scripts_glue" {
  for_each = fileset("${path.module}/../src/glue", "*.py")

  bucket = aws_s3_bucket.lake.id
  key    = "glue/scripts/${each.value}"
  source = "${path.module}/../src/glue/${each.value}"
  etag   = filemd5("${path.module}/../src/glue/${each.value}")
}

# Pacote src/ do pipeline: os jobs Silver e Gold baixam este zip em tempo
# de execução e importam os mesmos módulos de transformação usados na
# execução local — nenhuma lógica é duplicada nos scripts Glue.
data "archive_file" "src_pipeline" {
  type        = "zip"
  source_dir  = "${path.module}/../src"
  output_path = "${path.module}/build/src_pipeline.zip"
  excludes    = ["**/__pycache__/**"]
}

resource "aws_s3_object" "src_pipeline" {
  bucket = aws_s3_bucket.lake.id
  key    = "glue/scripts/src_pipeline.zip"
  source = data.archive_file.src_pipeline.output_path
  etag   = data.archive_file.src_pipeline.output_md5
}

# Consultas SQL da ingestão bronze, lidas pelo job em tempo de execução.
resource "aws_s3_object" "queries_bronze" {
  for_each = fileset("${path.module}/../queries/bronze", "*.sql")

  bucket = aws_s3_bucket.lake.id
  key    = "glue/queries/bronze/${each.value}"
  source = "${path.module}/../queries/bronze/${each.value}"
  etag   = filemd5("${path.module}/../queries/bronze/${each.value}")
}
