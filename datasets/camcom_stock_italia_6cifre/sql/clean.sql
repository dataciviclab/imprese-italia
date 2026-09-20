-- clean.sql: Stock Imprese Attive Italia 6 Cifre ATECO
-- CSV long nativo: Regione,Provincia,Settore,Divisione,Classe,Sottocategoria,Imprese Attive

SELECT
    normalize_string(Regione) AS regione,
    normalize_string(Provincia) AS provincia,
    normalize_string(Settore) AS settore,
    CAST(Divisione AS VARCHAR) AS divisione,
    CAST(Classe AS VARCHAR) AS classe,
    CAST(Sottocategoria AS VARCHAR) AS sottocategoria,
    CAST("Imprese Attive" AS BIGINT) AS imprese
FROM raw_input
WHERE "Imprese Attive" IS NOT NULL
  AND Regione IS NOT NULL
