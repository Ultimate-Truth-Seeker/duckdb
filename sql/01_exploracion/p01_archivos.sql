-- Objetivo: 3.1 cantidad de archivos Parquet disponibles, por tipo de taxi y anio (con subtotales y total).
-- Fuente: /workspace/data/raw/*/*/*.parquet
SELECT regexp_extract(file, 'raw/([^/]+)/', 1) AS tipo,
       regexp_extract(file, '/(\d{4})/', 1)    AS anio,
       count(*) AS archivos
FROM glob('/workspace/data/raw/*/*/*.parquet')
GROUP BY ROLLUP (tipo, anio)
ORDER BY tipo NULLS LAST, anio NULLS LAST;
