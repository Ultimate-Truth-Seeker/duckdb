-- Objetivo: 3.2 cantidad de registros disponibles, por tipo de taxi y anio de archivo (con subtotales y total).
-- Fuente: /workspace/data/raw/*/*/*.parquet
-- Decision: 121,184,384 viajes (yellow 119.6 M, green 1.59 M). coincide con verify_data.py y con la tabla trips. yellow es ~75 veces mas grande que green.
SELECT regexp_extract(filename, 'raw/([^/]+)/', 1) AS tipo,
       regexp_extract(filename, '/(\d{4})/', 1)    AS anio,
       count(*) AS registros
FROM read_parquet('/workspace/data/raw/*/*/*.parquet', union_by_name = true, filename = true)
GROUP BY ROLLUP (tipo, anio)
ORDER BY tipo NULLS LAST, anio NULLS LAST;
