-- clean.sql: Stock Imprese Attive Italia
-- CSV wide nativo: Territorio;Settore Ateco 2025;30/04/2025;... → long via UNPIVOT

WITH wide AS (
    SELECT "Territorio" AS territorio,
           COLUMNS('^Settore Ateco.*') AS ateco,
           COLUMNS('^[0-9]')
    FROM raw_input
),
long AS (
    UNPIVOT wide
    ON COLUMNS('^[0-9]')
    INTO NAME data VALUE imprese
),
typed AS (
    SELECT
        territorio,
        ateco,
        CAST(strptime(data, '%d/%m/%Y') AS DATE) AS data,
        TRY_CAST(imprese AS BIGINT) AS imprese
    FROM long
)
SELECT
    normalize_string(territorio) AS territorio,
    normalize_string(ateco) AS ateco,
    data,
    imprese
FROM typed
WHERE imprese IS NOT NULL
  AND territorio IS NOT NULL
  AND ateco IS NOT NULL
