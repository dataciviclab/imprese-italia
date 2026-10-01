-- clean.sql: Iscrizioni Imprese Italia
-- Nuove imprese iscritte al Registro per provincia x ATECO

SELECT
    normalize_string(territorio) AS territorio,
    normalize_string(ateco) AS ateco,
    -- data raw è 'YYYY-MM': allinea a fine mese come stock (DATE)
    CAST((CAST(data || '-01' AS DATE) + INTERVAL 1 MONTH - INTERVAL 1 DAY) AS DATE) AS data,
    CAST(nuove_imprese AS BIGINT) AS nuove_imprese
FROM raw_input
WHERE nuove_imprese IS NOT NULL
  AND territorio IS NOT NULL
  AND ateco IS NOT NULL
