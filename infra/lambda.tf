# Consumer serverless do streaming: Kinesis -> Lambda -> S3 bronze.
# O código-fonte vive no repositório (src/streaming/consumer_lambda.py).

resource "aws_iam_role" "lambda_consumer" {
  name = "${var.nome_projeto}-lambda-consumer"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect    = "Allow"
        Principal = { Service = "lambda.amazonaws.com" }
        Action    = "sts:AssumeRole"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_kinesis" {
  role       = aws_iam_role.lambda_consumer.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaKinesisExecutionRole"
}

resource "aws_iam_role_policy" "s3_put_bronze_streaming" {
  name = "s3-put-bronze-streaming"
  role = aws_iam_role.lambda_consumer.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = "s3:PutObject"
        Resource = "${aws_s3_bucket.lake.arn}/bronze/alunos_streaming/*"
      }
    ]
  })
}

data "archive_file" "consumer_lambda" {
  type        = "zip"
  source_file = "${path.module}/../src/streaming/consumer_lambda.py"
  output_path = "${path.module}/build/consumer_lambda.zip"
}

resource "aws_lambda_function" "consumer" {
  function_name = "${var.nome_projeto}-consumer"
  role          = aws_iam_role.lambda_consumer.arn
  handler       = "consumer_lambda.handler"
  runtime       = "python3.12"
  timeout       = 60
  memory_size   = 512

  filename         = data.archive_file.consumer_lambda.output_path
  source_code_hash = data.archive_file.consumer_lambda.output_base64sha256

  layers = [var.lambda_layer_pandas]

  environment {
    variables = {
      S3_BUCKET = aws_s3_bucket.lake.bucket
    }
  }
}

resource "aws_lambda_event_source_mapping" "kinesis" {
  event_source_arn                   = aws_kinesis_stream.eventos.arn
  function_name                      = aws_lambda_function.consumer.arn
  starting_position                  = "LATEST"
  batch_size                         = 100
  maximum_batching_window_in_seconds = 5
}
