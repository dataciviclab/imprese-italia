-- mart_serie_italia_ateco.sql: Serie mensile cancellazioni Italia x ATECO 2

SELECT
    data,
    ateco,
    cessazioni
FROM clean_input
WHERE territorio = 'ITALIA'
  AND ateco != 'TOTAL'
ORDER BY data, cessazioni DESC
