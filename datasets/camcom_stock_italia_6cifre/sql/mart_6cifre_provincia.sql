-- mart_6cifre_provincia.sql: Imprese attive per provincia x settore ATECO (2 cifre)

SELECT
    provincia,
    settore,
    SUM(imprese) AS imprese
FROM clean_input
GROUP BY provincia, settore
ORDER BY provincia, settore
