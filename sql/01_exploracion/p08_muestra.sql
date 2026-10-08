-- Objetivo: 3.5 muestra aleatoria de registros de cada tipo de taxi (las columnas exclusivas de un tipo quedan en NULL en el otro).
-- Fuente: /workspace/data/raw/yellow/*/*.parquet y /workspace/data/raw/green/*/*.parquet
-- Decision: la muestra confirma el esquema normalizado: zonas dentro de 1-265 y payment_type de 0 a 5 en yellow (1 a 5 y nulos en green). sin hallazgos adicionales.
SELECT 'yellow' AS tipo, * FROM (SELECT * FROM read_parquet('/workspace/data/raw/yellow/*/*.parquet', union_by_name = true) USING SAMPLE 5 ROWS)
UNION ALL BY NAME
SELECT 'green' AS tipo, * FROM (SELECT * FROM read_parquet('/workspace/data/raw/green/*/*.parquet', union_by_name = true) USING SAMPLE 5 ROWS);
