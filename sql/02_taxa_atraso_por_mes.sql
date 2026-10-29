-- 02: taxa de atraso por mês (prazo: entrega em até 3 dias após o envio)
-- Na base, o tempo entre envio e entrega vai de 0 a 4 dias, distribuído por igual.
SELECT
  DATE_TRUNC(DATE(created_at), MONTH) AS mes,
  COUNT(*) AS entregues,
  AVG(CASE WHEN TIMESTAMP_DIFF(delivered_at, shipped_at, DAY) > 3 THEN 1 ELSE 0 END) AS taxa_atraso
FROM `bigquery-public-data.thelook_ecommerce.orders`
WHERE created_at >= '2025-01-01' AND delivered_at IS NOT NULL
GROUP BY mes
ORDER BY mes;
