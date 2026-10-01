-- mart_serie_territorio.sql: Serie mensile stock per territorio (ATECO=TOTAL)
-- territorio_tipo: ITALIA | REGIONE | PROVINCIA (regioni = nome in maiuscolo)

SELECT
    data,
    territorio,
    CASE
        WHEN territorio = 'ITALIA' THEN 'ITALIA'
        WHEN territorio = upper(territorio) THEN 'REGIONE'
        ELSE 'PROVINCIA'
    END AS territorio_tipo,
    imprese
FROM clean_input
WHERE ateco = 'TOTAL'
ORDER BY data, territorio
