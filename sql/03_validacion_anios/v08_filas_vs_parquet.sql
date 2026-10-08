-- Objetivo: contrastar filas de la tabla contra las filas que reporta el footer de cada Parquet (5.6/5.7).
-- Devuelve 0 filas si coinciden. Ejecutar con duckdb desde la raiz del proyecto (ruta /workspace/data en el contenedor).
-- Fuente: vista `trips` = Parquet de data/raw/{yellow,green}/*/*.parquet normalizados (scripts/taxi_common.py), o la tabla `trips` de taxi.duckdb.
WITH pq AS (
    SELECT regexp_extract(file_name, '[^/\\]+$') AS source_file, num_rows AS filas_parquet
    FROM parquet_file_metadata('/workspace/data/raw/*/*/*.parquet'))
SELECT coalesce(pq.source_file, t.source_file) AS source_file, pq.filas_parquet, t.filas_trips
FROM pq FULL OUTER JOIN (SELECT source_file, count(*) AS filas_trips FROM trips GROUP BY 1) t USING (source_file)
WHERE pq.filas_parquet IS DISTINCT FROM t.filas_trips;
