-- mart_6cifre_regione.sql: Imprese attive per regione x settore ATECO (2 cifre)
-- Aggrega Divisione+Classe+Sottocategoria nel totale per settore

SELECT
    regione,
    settore,
    SUM(imprese) AS imprese
FROM clean_input
GROUP BY regione, settore
ORDER BY regione, settore
