# Infraestrutura AWS (IaC)

Provisionamento reproduzível da pipeline de streaming via CloudFormation:
Kinesis Data Stream + Lambda consumer + role IAM de menor privilégio.

## Pré-requisitos

- AWS CLI v2 configurado (`aws configure`)
- Bucket S3 do data lake já criado (o template não o cria para evitar
  exclusão acidental de dados no teardown)

## Deploy

```bash
# 1. Criar o bucket do data lake (uma única vez)
aws s3api create-bucket \
  --bucket SEU-BUCKET-DATA-LAKE \
  --region sa-east-1 \
  --create-bucket-configuration LocationConstraint=sa-east-1

# 2. Empacotar e subir o código do Lambda
cd ..
zip -j infra/consumer_lambda.zip src/streaming/consumer_lambda.py
aws s3 cp infra/consumer_lambda.zip s3://SEU-BUCKET-DATA-LAKE/infra/consumer_lambda.zip

# 3. Criar a stack
aws cloudformation deploy \
  --template-file infra/cloudformation.yaml \
  --stack-name fiap-alfabetizacao-streaming \
  --capabilities CAPABILITY_NAMED_IAM \
  --parameter-overrides \
      NomeBucketDataLake=SEU-BUCKET-DATA-LAKE \
      CodigoS3Bucket=SEU-BUCKET-DATA-LAKE
```

## Testar

```bash
# Enviar eventos reais ao stream (do diretório raiz do projeto)
python -m src.streaming.producer --destino kinesis --total-eventos 500

# Acompanhar o processamento
aws logs tail /aws/lambda/fiap-alfabetizacao-stream-consumer --follow --region sa-east-1

# Conferir os arquivos gravados pelo Lambda
aws s3 ls s3://SEU-BUCKET-DATA-LAKE/bronze/alunos_streaming/ --recursive
```

## Teardown (zerar custos)

O único custo fixo da stack é o shard do Kinesis (~US$ 0,02/hora).
Após coletar as evidências:

```bash
aws cloudformation delete-stack --stack-name fiap-alfabetizacao-streaming
```

O bucket (e os dados do lake) são preservados. Para remover tudo:

```bash
aws s3 rb s3://SEU-BUCKET-DATA-LAKE --force
```
