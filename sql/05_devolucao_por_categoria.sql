-- 05: taxa de devolução por categoria (itens cancelados fora da conta)
-- Achado: as categorias grandes têm taxas parecidas (~10%). As diferenças maiores
-- aparecem nas categorias com poucos itens (ex.: Clothing Sets, 182 itens), por acaso.
SELECT
  p.category AS categoria,
  COUNT(*) AS itens_vendidos,
  ROUND(AVG(CASE WHEN oi.status = 'Returned' THEN 1 ELSE 0 END), 3) AS taxa_devolucao
FROM `bigquery-public-data.thelook_ecommerce.order_items` AS oi
JOIN `bigquery-public-data.thelook_ecommerce.products` AS p ON oi.product_id = p.id
WHERE oi.created_at >= '2025-01-01'
  AND oi.status != 'Cancelled'
GROUP BY categoria
ORDER BY taxa_devolucao DESC;
