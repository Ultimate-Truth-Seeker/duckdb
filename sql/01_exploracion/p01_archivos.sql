-- Objetivo: 3.1 cantidad de archivos Parquet disponibles, por tipo de taxi y anio (con subtotales y total).
-- Fuente: /workspace/data/raw/*/*/*.parquet
-- Decision: 64 archivos (32 por tipo): 12 meses de 2024 y 2025 y 8 de 2026. el resto de 2026 aun no esta publicado, asi que 2026 se trata como incompleto.
SELECT regexp_extract(file, 'raw/([^/]+)/', 1) AS tipo,
       regexp_extract(file, '/(\d{4})/', 1)    AS anio,
       count(*) AS archivos
FROM glob('/workspace/data/raw/*/*/*.parquet')
GROUP BY ROLLUP (tipo, anio)
ORDER BY tipo NULLS LAST, anio NULLS LAST;
