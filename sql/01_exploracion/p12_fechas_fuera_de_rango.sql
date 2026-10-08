-- Objetivo: 3.6 distribucion de los anios de recogida por tipo: revela fechas imposibles (p. ej. 2002 o 2009) dentro de archivos de 2024-2026.
-- Fuente: /workspace/data/raw/yellow/*/*.parquet y /workspace/data/raw/green/*/*.parquet
-- Decision: hay recogidas de 2001, 2002, 2007, 2008, 2009 y 2023 (pocas decenas de viajes por tipo). se excluyen del analisis temporal con el filtro 2024-2026.
SELECT 'yellow' AS tipo, year(tpep_pickup_datetime) AS anio_recogida, count(*) AS registros
FROM read_parquet('/workspace/data/raw/yellow/*/*.parquet', union_by_name = true) GROUP BY ALL
UNION ALL
SELECT 'green', year(lpep_pickup_datetime), count(*)
FROM read_parquet('/workspace/data/raw/green/*/*.parquet', union_by_name = true) GROUP BY ALL
ORDER BY tipo, anio_recogida;
