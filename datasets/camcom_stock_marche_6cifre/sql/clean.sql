-- clean.sql: Stock Imprese Attive Marche 6 Cifre ATECO
-- CSV long nativo: Provincia,Comune,Settore,Divisione,Classe,Sottocategoria,Imprese Attive

SELECT
    normalize_string(Provincia) AS provincia,
    normalize_string(Comune) AS comune,
    normalize_string(Settore) AS settore,
    CAST(Divisione AS VARCHAR) AS divisione,
    CAST(Classe AS VARCHAR) AS classe,
    CAST(Sottocategoria AS VARCHAR) AS sottocategoria,
    CAST("Imprese Attive" AS BIGINT) AS imprese
FROM raw_input
WHERE "Imprese Attive" IS NOT NULL
  AND Provincia IS NOT NULL
