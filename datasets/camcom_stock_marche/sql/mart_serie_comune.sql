-- mart_serie_comune.sql: Serie mensile stock comuni Marche (ATECO=TOTAL)

SELECT
    data,
    territorio,
    imprese
FROM clean_input
WHERE ateco = 'TOTAL'
ORDER BY data, territorio
