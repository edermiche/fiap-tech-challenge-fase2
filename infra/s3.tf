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

# Consultas SQL da ingestão bronze, lidas pelo job em tempo de execução.
resource "aws_s3_object" "queries_bronze" {
  for_each = fileset("${path.module}/../queries/bronze", "*.sql")

  bucket = aws_s3_bucket.lake.id
  key    = "glue/queries/bronze/${each.value}"
  source = "${path.module}/../queries/bronze/${each.value}"
  etag   = filemd5("${path.module}/../queries/bronze/${each.value}")
}
