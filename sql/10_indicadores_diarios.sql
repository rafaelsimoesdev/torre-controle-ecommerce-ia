-- 10: tabela de indicadores diários da operação (uma linha por dia, a partir de 2025)
-- Regras: receita e devolução sem itens cancelados; atraso = entrega > 3 dias após o envio.
-- O dia de hoje fica de fora por estar incompleto.
CREATE SCHEMA IF NOT EXISTS torre_controle OPTIONS (location = 'US');

CREATE OR REPLACE TABLE torre_controle.indicadores_diarios AS
WITH pedidos AS (
  SELECT
    DATE(created_at) AS dia,
    COUNT(*) AS pedidos,
    COUNTIF(status = 'Cancelled') AS cancelados
  FROM `bigquery-public-data.thelook_ecommerce.orders`
  GROUP BY dia
),
vendas AS (
  SELECT
    DATE(created_at) AS dia,
    ROUND(SUM(CASE WHEN status NOT IN ('Cancelled', 'Returned') THEN sale_price END), 2) AS receita,
    COUNT(DISTINCT CASE WHEN status NOT IN ('Cancelled', 'Returned') THEN order_id END) AS pedidos_validos,
    COUNTIF(status != 'Cancelled') AS itens_vendidos,
    SAFE_DIVIDE(COUNTIF(status = 'Returned'), COUNTIF(status != 'Cancelled')) AS taxa_devolucao
  FROM `bigquery-public-data.thelook_ecommerce.order_items`
  GROUP BY dia
),
entregas AS (
  SELECT
    DATE(delivered_at) AS dia,
    COUNT(*) AS entregues,
    AVG(CASE WHEN TIMESTAMP_DIFF(delivered_at, shipped_at, DAY) > 3 THEN 1 ELSE 0 END) AS taxa_atraso
  FROM `bigquery-public-data.thelook_ecommerce.orders`
  WHERE delivered_at IS NOT NULL
  GROUP BY dia
)
SELECT
  p.dia,
  p.pedidos,
  p.cancelados,
  v.receita,
  ROUND(SAFE_DIVIDE(v.receita, v.pedidos_validos), 2) AS ticket_medio,
  v.itens_vendidos,
  ROUND(v.taxa_devolucao, 4) AS taxa_devolucao,
  e.entregues,
  ROUND(e.taxa_atraso, 4) AS taxa_atraso
FROM pedidos AS p
LEFT JOIN vendas AS v USING (dia)
LEFT JOIN entregas AS e USING (dia)
WHERE p.dia >= '2025-01-01'
  AND p.dia < CURRENT_DATE()
ORDER BY p.dia;
