SELECT
    ano_competencia,
    id_municipio,
    sigla_uf,
    COUNT(1) AS total_beneficiarios,
    SUM(valor_parcela) AS valor_total_pago
FROM `basedosdados.br_cgu_beneficios_cidadao.novo_bolsa_familia`
WHERE ano_competencia BETWEEN 2022 AND 2024
GROUP BY ano_competencia, id_municipio, sigla_uf
