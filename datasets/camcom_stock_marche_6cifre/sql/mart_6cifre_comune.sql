-- mart_6cifre_comune.sql: Imprese attive per comune Marche x settore ATECO (2 cifre)

SELECT
    comune,
    provincia,
    settore,
    SUM(imprese) AS imprese
FROM clean_input
GROUP BY comune, provincia, settore
ORDER BY comune, provincia, settore
