-- Objetivo: 5.6 comprobar, leyendo directamente los Parquet con un comodin, que se pueden consultar juntos 2024, 2025 y 2026
-- (archivos, registros y rango de fechas por anio y tipo). Sin tabla materializada.
-- Fuente: /workspace/data/raw/*/*/*.parquet
-- Decision: una sola consulta con comodin lee 2024, 2025 y 2026 de ambos tipos (6 filas). los anios se pueden consultar juntos sin cambiar nada.
SELECT regexp_extract(filename, 'raw/([^/]+)/', 1) AS tipo,
       regexp_extract(filename, '/(\d{4})/', 1)    AS anio,
       count(DISTINCT filename) AS archivos,
       count(*) AS registros,
       min(coalesce(tpep_pickup_datetime, lpep_pickup_datetime)) AS primera_recogida,
       max(coalesce(tpep_pickup_datetime, lpep_pickup_datetime)) AS ultima_recogida
FROM read_parquet('/workspace/data/raw/*/*/*.parquet', union_by_name = true, filename = true)
GROUP BY ALL
ORDER BY tipo, anio;
