-- Objetivo: 3.3 comparar las columnas de yellow y green (cuales son comunes, cuales exclusivas y si cambia el tipo).
-- Fuente: /workspace/data/raw/yellow/*/*.parquet y /workspace/data/raw/green/*/*.parquet
WITH y AS (SELECT lower(column_name) AS col, column_name AS nombre_yellow, column_type AS tipo_yellow
           FROM (DESCRIBE SELECT * FROM read_parquet('/workspace/data/raw/yellow/*/*.parquet', union_by_name = true))),
     g AS (SELECT lower(column_name) AS col, column_name AS nombre_green, column_type AS tipo_green
           FROM (DESCRIBE SELECT * FROM read_parquet('/workspace/data/raw/green/*/*.parquet', union_by_name = true)))
SELECT coalesce(y.col, g.col) AS columna, nombre_yellow, tipo_yellow, nombre_green, tipo_green,
       CASE WHEN y.col IS NULL THEN 'solo green' WHEN g.col IS NULL THEN 'solo yellow'
            WHEN tipo_yellow = tipo_green THEN 'comun' ELSE 'comun, tipo distinto' END AS situacion
FROM y FULL OUTER JOIN g ON y.col = g.col
ORDER BY situacion, columna;
