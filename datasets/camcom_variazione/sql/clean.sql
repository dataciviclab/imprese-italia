-- clean.sql: Variazione % Tendenziale Imprese Attive Italia
-- CSV wide nativo: Territorio;Settore Ateco 2025;30/04/2025;... → long via UNPIVOT
-- Le celle vuote (mesi non ancora rilevati) diventano NULL.

WITH wide AS (
    SELECT "Territorio" AS territorio,
           COLUMNS('^Settore Ateco.*') AS ateco,
           COLUMNS('^[0-9]')
    FROM raw_input
),
long AS (
    UNPIVOT wide
    ON COLUMNS('^[0-9]')
    INTO NAME data VALUE variazione_pct
),
typed AS (
    SELECT
        territorio,
        ateco,
        CAST(strptime(data, '%d/%m/%Y') AS DATE) AS data,
        TRY_CAST(variazione_pct AS DOUBLE) AS variazione_pct
    FROM long
)
SELECT
    normalize_string(territorio) AS territorio,
    normalize_string(ateco) AS ateco,
    data,
    variazione_pct
FROM typed
WHERE variazione_pct IS NOT NULL
  AND territorio IS NOT NULL
  AND ateco IS NOT NULL
