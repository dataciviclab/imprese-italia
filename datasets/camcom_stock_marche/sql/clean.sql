-- clean.sql: Stock Imprese Attive Marche
-- CSV long (unpivot dal download script): territorio,ateco,data,imprese

SELECT
    normalize_string(territorio) AS territorio,
    normalize_string(ateco) AS ateco,
    data,
    CAST(imprese AS BIGINT) AS imprese
FROM raw_input
WHERE imprese IS NOT NULL
  AND territorio IS NOT NULL
  AND ateco IS NOT NULL
