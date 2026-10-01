-- mart_specializzazione.sql: RCA Marche vs Italia per ATECO (ultimo mese stock)
-- rca = (share Marche) / (share Italia); >1 = sovrarappresentato nelle Marche

WITH latest AS (
    SELECT MAX(data) AS data_rif
    FROM read_parquet('{support.stock_italia.clean}')
    WHERE territorio = 'ITALIA'
),
marche AS (
    SELECT
        s.ateco,
        SUM(s.imprese) AS stock_marche
    FROM read_parquet('{support.stock_marche.clean}') s
    CROSS JOIN latest l
    WHERE s.data = l.data_rif
      AND s.ateco != 'TOTAL'
    GROUP BY s.ateco
),
italia AS (
    SELECT
        s.ateco,
        SUM(s.imprese) AS stock_italia
    FROM read_parquet('{support.stock_italia.clean}') s
    CROSS JOIN latest l
    WHERE s.data = l.data_rif
      AND s.territorio = 'ITALIA'
      AND s.ateco != 'TOTAL'
    GROUP BY s.ateco
)
SELECT
    l.data_rif AS data,
    m.ateco,
    m.stock_marche,
    i.stock_italia,
    ROUND(100.0 * m.stock_marche / NULLIF(SUM(m.stock_marche) OVER (), 0), 2) AS share_marche_pct,
    ROUND(100.0 * i.stock_italia / NULLIF(SUM(i.stock_italia) OVER (), 0), 2) AS share_italia_pct,
    ROUND(
        (m.stock_marche / NULLIF(SUM(m.stock_marche) OVER (), 0))
        / NULLIF(i.stock_italia / NULLIF(SUM(i.stock_italia) OVER (), 0), 0),
        3
    ) AS rca
FROM marche m
INNER JOIN italia i ON m.ateco = i.ateco
CROSS JOIN latest l
ORDER BY rca DESC
