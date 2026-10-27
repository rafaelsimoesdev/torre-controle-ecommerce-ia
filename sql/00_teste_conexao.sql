-- Primeira consulta: quantos pedidos existem e de quando até quando
SELECT
  COUNT(*) AS pedidos,
  MIN(created_at) AS primeiro_pedido,
  MAX(created_at) AS ultimo_pedido
FROM `bigquery-public-data.thelook_ecommerce.orders`;
