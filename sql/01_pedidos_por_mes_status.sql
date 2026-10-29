-- 01: pedidos por mês e status, a partir de 2025
SELECT
  DATE_TRUNC(DATE(created_at), MONTH) AS mes,
  status,
  COUNT(*) AS pedidos
FROM `bigquery-public-data.thelook_ecommerce.orders`
WHERE created_at >= '2025-01-01'
GROUP BY mes, status
ORDER BY mes, status;
