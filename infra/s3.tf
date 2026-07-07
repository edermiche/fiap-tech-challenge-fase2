# Data lake em camadas (bronze/silver/gold) — equivalente ao data/ local.

resource "aws_s3_bucket" "lake" {
  bucket = var.bucket_lake
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
