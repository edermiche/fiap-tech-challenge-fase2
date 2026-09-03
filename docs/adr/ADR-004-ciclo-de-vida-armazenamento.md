# ADR-004 — Ciclo de vida do armazenamento no S3

- **Status**: aceito
- **Data**: 2026-09-02
- **Decisores**: time do Tech Challenge Fase 2

## Contexto

O FinOps do projeto cobria custo de consulta (parquet + partição + `dry run`
com `maximum_bytes_billed`) e custo de compute (serverless, Python Shell,
micro-lotes). Faltava o armazenamento.

A Bronze guarda **todo** o histórico particionado por `execution_date`, e cada
reprocessamento acrescenta uma partição nova sem que nada expire. Hoje são
~141 MB e ninguém sente. Com o EventBridge Scheduler semanal ligado
(`infra/scheduler.tf`), são ~52 cargas por ano; a conta cresce sozinha, de
forma monotônica, e ninguém volta para limpar. Era o único vazamento de custo
que restava na arquitetura.

## Decisão

Declarar o ciclo de vida no próprio `infra/s3.tf`
(`aws_s3_bucket_lifecycle_configuration.lake`), com os prazos em variáveis:

| Regra | Prefixo | Ação |
|---|---|---|
| `bronze-historico` | `bronze/` | Standard-IA aos 30 dias → Glacier Instant Retrieval aos 90 → expira aos 730 |
| `silver-execucoes-antigas` | `silver/` | Standard-IA aos 90 dias, sem expiração |
| `abortar-uploads-incompletos` | todo o bucket | Aborta upload multipart interrompido após 7 dias |

Variáveis: `dias_bronze_standard_ia`, `dias_bronze_glacier_ir`,
`dias_bronze_expiracao`, `dias_silver_standard_ia` (`infra/variables.tf`).

## Justificativa das escolhas

**Por que Glacier Instant Retrieval e não Glacier Flexible / Deep Archive.**
A razão de guardar a Bronze é reprocessar a partir do dado bruto. Com IR, a
leitura continua em milissegundos e um reprocessamento antigo funciona sem job
de restore; com Flexible ou Deep Archive, a economia seria maior, mas o
reprocessamento passaria a exigir uma etapa de restore de horas — o que
esvazia o motivo de manter a Bronze.

**Por que a Bronze expira e a Silver não.** A Bronze é reproduzível: as
consultas estão em `queries/bronze/*.sql` e a fonte é pública. Dois anos de
histórico bruto cobrem qualquer auditoria plausível deste projeto. A Silver
apenas esfria: a execução corrente é o que a Gold lê, e execuções antigas
raramente são consultadas — mas apagá-las quebraria a comparação entre safras
que o [ADR-002](ADR-002-gate-de-qualidade.md) introduziu.

**Por que a Gold fica fora.** É o que os dashboards leem a cada acesso, é a
menor das três camadas, e `metricas_qualidade` precisa do histórico completo
para a comparação entre safras. Esfriar aqui trocaria centavos de
armazenamento por latência de leitura e custo de recuperação.

**Objeto pequeno não transiciona.** A AWS não move para IA objetos menores que
128 KB e cobra o mínimo de 128 KB por objeto nessa classe. As dimensões
pequenas do lake continuam em Standard — a economia vem das partições grandes
de fato, que é onde o volume está.

## Consequências

- O crescimento da Bronze passa a ser limitado por política, não por
  disciplina de quem lembra de limpar.
- Reprocessar a partir de uma partição Bronze com mais de 2 anos deixa de ser
  possível — aceito, porque a extração é reproduzível a partir da fonte.
- Objeto que sai do Standard-IA antes de 30 dias é cobrado como se tivesse
  ficado 30 (mínimo da classe); com transição só aos 30 dias e expiração aos
  730, não caímos nesse caso.
- A transição em si tem custo por objeto (por milhares de requisições). No
  nosso volume — dezenas de arquivos por carga — é desprezível, mas seria um
  ponto de atenção se a Bronze passasse a gerar milhares de arquivos pequenos
  por execução.

## Não aplicado neste ciclo

O `terraform apply` **não** foi executado: a mudança está declarada no código
e versionada, mas a infraestrutura AWS não foi atualizada nesta rodada. Para
aplicar:

```bash
cd infra
terraform plan    # a mudança esperada é só a criação do lifecycle configuration
terraform apply
```
