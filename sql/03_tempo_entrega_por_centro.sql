-- 03: tempo médio entre envio e entrega por centro de distribuição
-- Resultado: todos os centros ficam em ~2,0 dias. O tempo de entrega é sorteado
-- pelo gerador da base e não depende do centro, então não dá para prevê-lo.
SELECT
  dc.name AS centro,
  COUNT(DISTINCT o.order_id) AS pedidos,
  ROUND(AVG(TIMESTAMP_DIFF(o.delivered_at, o.shipped_at, DAY)), 2) AS media_dias
FROM `bigquery-public-data.thelook_ecommerce.orders` AS o
JOIN `bigquery-public-data.thelook_ecommerce.order_items` AS oi ON oi.order_id = o.order_id
JOIN `bigquery-public-data.thelook_ecommerce.products` AS p ON p.id = oi.product_id
JOIN `bigquery-public-data.thelook_ecommerce.distribution_centers` AS dc ON dc.id = p.distribution_center_id
WHERE o.delivered_at IS NOT NULL
GROUP BY centro
ORDER BY media_dias DESC;
