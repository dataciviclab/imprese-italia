-- mart_bilancio_mensile.sql: Bilancio demografico Italia x ATECO x mese
-- stock + iscrizioni + cessazioni + netto (cross-dataset via support clean)

WITH stock AS (
    SELECT
        data,
        ateco,
        imprese AS stock
    FROM read_parquet('{support.stock_italia.clean}')
    WHERE territorio = 'ITALIA'
      AND ateco != 'TOTAL'
),
iscrizioni AS (
    SELECT
        data,
        ateco,
        nuove_imprese AS iscrizioni
    FROM read_parquet('{support.iscrizioni.clean}')
    WHERE territorio = 'ITALIA'
      AND ateco != 'TOTAL'
),
cancellazioni AS (
    SELECT
        data,
        ateco,
        cessazioni
    FROM read_parquet('{support.cancellazioni.clean}')
    WHERE territorio = 'ITALIA'
      AND ateco != 'TOTAL'
)
SELECT
    s.data,
    s.ateco,
    s.stock,
    i.iscrizioni,
    c.cessazioni,
    i.iscrizioni - c.cessazioni AS netto,
    ROUND(100.0 * (i.iscrizioni - c.cessazioni) / NULLIF(s.stock, 0), 3) AS netto_pct_stock
FROM stock s
LEFT JOIN iscrizioni i ON s.data = i.data AND s.ateco = i.ateco
LEFT JOIN cancellazioni c ON s.data = c.data AND s.ateco = c.ateco
ORDER BY s.data, s.ateco
