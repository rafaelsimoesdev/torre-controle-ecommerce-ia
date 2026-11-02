-- RFM por cliente: Recência, Frequência e Valor (Monetary).
-- Data de referência: 22/10/2026, o último dia antes do salto artificial da base.
-- Pedidos cancelados ou devolvidos não contam como compra.

CREATE OR REPLACE TABLE torre_controle.rfm_clientes AS

WITH compras AS (
  -- uma linha por pedido válido, com o valor total do pedido
  SELECT
    user_id,
    order_id,
    MIN(created_at) AS criado_em,
    SUM(sale_price) AS valor_pedido
  FROM `bigquery-public-data.thelook_ecommerce.order_items`
  WHERE status NOT IN ('Cancelled', 'Returned')
    AND DATE(created_at) <= '2026-10-22'
  GROUP BY user_id, order_id
)

SELECT
  user_id,
  -- R: dias entre a última compra e a data de referência
  DATE_DIFF(DATE '2026-10-22', DATE(MAX(criado_em)), DAY) AS recencia,
  -- TODO 1 (F): quantos pedidos diferentes o cliente fez
  COUNT(*) AS frequencia,
  -- TODO 2 (M): quanto o cliente gastou no total, arredondado com 2 casas
  ROUND(SUM(valor_pedido), 2) AS valor
FROM compras
GROUP BY user_id
