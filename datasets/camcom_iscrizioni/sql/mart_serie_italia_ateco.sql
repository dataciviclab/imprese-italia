-- mart_serie_italia_ateco.sql: Serie mensile iscrizioni Italia x ATECO 2

SELECT
    data,
    ateco,
    nuove_imprese
FROM clean_input
WHERE territorio = 'ITALIA'
  AND ateco != 'TOTAL'
ORDER BY data, nuove_imprese DESC
