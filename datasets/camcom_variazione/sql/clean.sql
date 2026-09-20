-- clean.sql: Variazione % Tendenziale Imprese Attive Italia
-- CSV long (unpivot dal download script): territorio,ateco,data,variazione_pct

SELECT
    normalize_string(territorio) AS territorio,
    normalize_string(ateco) AS ateco,
    data,
    CAST(variazione_pct AS DOUBLE) AS variazione_pct
FROM raw_input
WHERE variazione_pct IS NOT NULL
  AND territorio IS NOT NULL
  AND ateco IS NOT NULL
