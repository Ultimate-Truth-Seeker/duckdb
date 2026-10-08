-- Objetivo: 3.3 / 3.6 columnas que NO estan presentes en todos los archivos de un tipo (esquema que evoluciona entre meses/anios).
-- Fuente: /workspace/data/raw/*/*/*.parquet
WITH s AS (
    SELECT regexp_extract(file_name, 'raw/([^/]+)/', 1) AS tipo, lower(name) AS columna, file_name
    FROM parquet_schema('/workspace/data/raw/*/*/*.parquet') WHERE num_children IS NULL),
total AS (SELECT tipo, count(DISTINCT file_name) AS archivos_tipo FROM s GROUP BY tipo)
SELECT s.tipo, s.columna, count(DISTINCT s.file_name) AS archivos_con_columna, any_value(t.archivos_tipo) AS archivos_del_tipo,
       min(regexp_extract(s.file_name, '(\d{4}-\d{2})\.parquet', 1)) AS primer_mes_con_columna
FROM s JOIN total t USING (tipo)
GROUP BY s.tipo, s.columna
HAVING count(DISTINCT s.file_name) < any_value(t.archivos_tipo)
ORDER BY s.tipo, s.columna;
