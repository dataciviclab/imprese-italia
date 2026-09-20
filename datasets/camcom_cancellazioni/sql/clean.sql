-- clean.sql: Cancellazioni Imprese Italia
-- Imprese cancellate dal Registro per provincia x ATECO

SELECT
    normalize_string(territorio) AS territorio,
    normalize_string(ateco) AS ateco,
    data,
    CAST(cessazioni AS BIGINT) AS cessazioni
FROM raw_input
WHERE cessazioni IS NOT NULL
  AND territorio IS NOT NULL
  AND ateco IS NOT NULL
