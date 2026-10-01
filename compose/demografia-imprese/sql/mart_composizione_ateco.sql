-- mart_composizione_ateco.sql: Share % stock per ATECO x territorio x mese
-- territorio_tipo: ITALIA | REGIONE | PROVINCIA

WITH base AS (
    SELECT
        data,
        territorio,
        CASE
            WHEN territorio = 'ITALIA' THEN 'ITALIA'
            WHEN territorio = upper(territorio) THEN 'REGIONE'
            ELSE 'PROVINCIA'
        END AS territorio_tipo,
        ateco,
        imprese
    FROM read_parquet('{support.stock_italia.clean}')
    WHERE ateco != 'TOTAL'
),
tot AS (
    SELECT
        data,
        territorio,
        SUM(imprese) AS totale
    FROM base
    GROUP BY data, territorio
)
SELECT
    b.data,
    b.territorio,
    b.territorio_tipo,
    b.ateco,
    b.imprese,
    t.totale,
    ROUND(100.0 * b.imprese / NULLIF(t.totale, 0), 2) AS share_pct
FROM base b
INNER JOIN tot t ON b.data = t.data AND b.territorio = t.territorio
ORDER BY b.data, b.territorio, b.imprese DESC
