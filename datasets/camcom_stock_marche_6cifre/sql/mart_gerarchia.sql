-- mart_gerarchia.sql: Stock Marche con gerarchia ATECO completa per comune
-- Non aggrega al settore: preserva divisione/classe/sottocategoria per micro-analisi.

SELECT
    provincia,
    comune,
    settore,
    divisione,
    classe,
    sottocategoria,
    imprese
FROM clean_input
WHERE provincia IS NOT NULL
  AND comune IS NOT NULL
  AND imprese IS NOT NULL
ORDER BY provincia, comune, settore, divisione, classe, sottocategoria
