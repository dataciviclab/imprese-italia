-- mart_gerarchia.sql: Stock Italia con gerarchia ATECO completa
-- Non aggrega al settore: preserva divisione/classe/sottocategoria per micro-analisi.

SELECT
    regione,
    provincia,
    settore,
    divisione,
    classe,
    sottocategoria,
    imprese
FROM clean_input
WHERE regione IS NOT NULL
  AND imprese IS NOT NULL
ORDER BY regione, provincia, settore, divisione, classe, sottocategoria
