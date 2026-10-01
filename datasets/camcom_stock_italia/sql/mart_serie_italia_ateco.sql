-- mart_serie_italia_ateco.sql: Serie mensile stock Italia x ATECO 2
-- Include share % sul totale nazionale (escluso TOTAL) per composizione.

WITH base AS (
    SELECT
        data,
        ateco,
        imprese
    FROM clean_input
    WHERE territorio = 'ITALIA'
      AND ateco != 'TOTAL'
),
tot AS (
    SELECT
        data,
        SUM(imprese) AS totale
    FROM base
    GROUP BY data
)
SELECT
    b.data,
    b.ateco,
    b.imprese,
    t.totale,
    ROUND(100.0 * b.imprese / NULLIF(t.totale, 0), 2) AS share_pct
FROM base b
INNER JOIN tot t ON b.data = t.data
ORDER BY b.data, b.imprese DESC
