-- 04: receita e ticket médio por mês (sem itens cancelados ou devolvidos)
-- O último mês aparece menor por estar incompleto.
SELECT
  DATE_TRUNC(DATE(created_at), MONTH) AS mes,
  ROUND(SUM(sale_price), 2) AS receita,
  COUNT(DISTINCT order_id) AS pedidos,
  ROUND(SAFE_DIVIDE(SUM(sale_price), COUNT(DISTINCT order_id)), 2) AS ticket_medio
FROM `bigquery-public-data.thelook_ecommerce.order_items`
WHERE created_at >= '2025-01-01'
  AND status NOT IN ('Cancelled', 'Returned')
GROUP BY mes
ORDER BY mes;
