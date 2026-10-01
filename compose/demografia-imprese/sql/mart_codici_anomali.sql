-- mart_codici_anomali.sql: Stock Italia ultimo mese con flag codici ATECO speciali
-- X/V/U/P sono codici rari/non standard nella fonte camcom: da escludere dai
-- ranking principali o mostrare con caveat nella UI.

WITH latest AS (
    SELECT MAX(data) AS data_rif
    FROM read_parquet('{support.stock_italia.clean}')
    WHERE territorio = 'ITALIA'
)
SELECT
    s.data,
    s.ateco,
    s.imprese AS stock,
    v.variazione_pct,
    s.ateco IN ('X', 'V', 'U', 'P') AS is_codice_speciale,
    CASE
        WHEN s.ateco IN ('X', 'V', 'U', 'P') THEN 'codice_speciale_raro'
        WHEN s.ateco = 'TOTAL' THEN 'aggregato'
        ELSE 'standard'
    END AS classe_ateco
FROM read_parquet('{support.stock_italia.clean}') s
LEFT JOIN read_parquet('{support.variazione.clean}') v
    ON s.territorio = v.territorio
   AND s.ateco = v.ateco
   AND s.data = v.data
CROSS JOIN latest l
WHERE s.territorio = 'ITALIA'
  AND s.data = l.data_rif
ORDER BY s.imprese DESC
