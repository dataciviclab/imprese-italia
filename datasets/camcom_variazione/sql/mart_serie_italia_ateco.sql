-- mart_serie_italia_ateco.sql: Serie mensile variazione % YoY Italia x ATECO 2

SELECT
    data,
    ateco,
    variazione_pct
FROM clean_input
WHERE territorio = 'ITALIA'
  AND ateco != 'TOTAL'
ORDER BY data, variazione_pct DESC
