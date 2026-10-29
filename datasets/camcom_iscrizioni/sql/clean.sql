-- clean.sql: Iscrizioni Imprese Italia
-- CSV wide nativo: Territorio;Settore Ateco 2025;YYYY-MM;... → long via UNPIVOT

WITH wide AS (
    SELECT "Territorio" AS territorio,
           COLUMNS('^Settore Ateco.*') AS ateco,
           COLUMNS('^[0-9]')
    FROM raw_input
),
long AS (
    UNPIVOT wide
    ON COLUMNS('^[0-9]')
    INTO NAME data VALUE nuove_imprese
),
typed AS (
    SELECT
        territorio,
        ateco,
        -- data raw è 'YYYY-MM': allinea a fine mese come stock (DATE)
        CAST((CAST(data || '-01' AS DATE) + INTERVAL 1 MONTH - INTERVAL 1 DAY) AS DATE) AS data,
        TRY_CAST(nuove_imprese AS BIGINT) AS nuove_imprese
    FROM long
)
SELECT
    normalize_string(territorio) AS territorio,
    normalize_string(ateco) AS ateco,
    data,
    nuove_imprese
FROM typed
WHERE nuove_imprese IS NOT NULL
  AND territorio IS NOT NULL
  AND ateco IS NOT NULL
