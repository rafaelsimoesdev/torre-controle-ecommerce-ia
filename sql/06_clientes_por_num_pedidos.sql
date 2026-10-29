-- 06: clientes por número de pedidos (pedidos cancelados fora da conta)
-- Achado: 66,5% dos clientes compram uma vez só; ninguém passa de 4 pedidos.
WITH pedidos_por_cliente AS (
  SELECT
    user_id,
    COUNT(*) AS num_pedidos
  FROM `bigquery-public-data.thelook_ecommerce.orders`
  WHERE status != 'Cancelled'
  GROUP BY user_id
)
SELECT
  num_pedidos,
  COUNT(*) AS clientes
FROM pedidos_por_cliente
GROUP BY num_pedidos
ORDER BY num_pedidos;
