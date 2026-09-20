-- mart_provincia_ateco.sql: Imprese attive per provincia x ATECO
-- Ultima rilevazione disponibile per ogni combinazione

WITH latest AS (
    SELECT
        territorio,
        ateco,
        MAX(data) AS data
    FROM clean_input
    GROUP BY territorio, ateco
)
SELECT
    l.territorio,
    l.ateco,
    c.data,
    c.imprese
FROM clean_input c
INNER JOIN latest l
    ON c.territorio = l.territorio
    AND c.ateco = l.ateco
    AND c.data = l.data
ORDER BY l.territorio, l.ateco
