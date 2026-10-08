-- Objetivo: 3.2 cantidad de registros disponibles, por tipo de taxi y anio de archivo (con subtotales y total).
-- Fuente: /workspace/data/raw/*/*/*.parquet
SELECT regexp_extract(filename, 'raw/([^/]+)/', 1) AS tipo,
       regexp_extract(filename, '/(\d{4})/', 1)    AS anio,
       count(*) AS registros
FROM read_parquet('/workspace/data/raw/*/*/*.parquet', union_by_name = true, filename = true)
GROUP BY ROLLUP (tipo, anio)
ORDER BY tipo NULLS LAST, anio NULLS LAST;
