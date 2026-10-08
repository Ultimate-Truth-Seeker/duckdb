-- Objetivo: 3.4 / 3.6 detectar columnas cuyo tipo fisico en Parquet cambia de un archivo a otro (riesgo al combinar archivos).
-- Fuente: /workspace/data/raw/*/*/*.parquet
-- Decision: 0 filas: ninguna columna cambia de tipo fisico entre archivos. se deja TRY_CAST igual por seguridad, pero hoy no hay conflicto de tipos.
WITH s AS (
    SELECT regexp_extract(file_name, 'raw/([^/]+)/', 1) AS tipo, lower(name) AS columna, type AS tipo_parquet, file_name
    FROM parquet_schema('/workspace/data/raw/*/*/*.parquet')
    WHERE num_children IS NULL)
SELECT tipo, columna, list(DISTINCT tipo_parquet ORDER BY tipo_parquet) AS tipos_encontrados,
       count(DISTINCT file_name) AS archivos_con_la_columna
FROM s
GROUP BY tipo, columna
HAVING count(DISTINCT tipo_parquet) > 1
ORDER BY tipo, columna;
