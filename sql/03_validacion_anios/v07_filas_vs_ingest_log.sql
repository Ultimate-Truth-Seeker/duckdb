-- Objetivo: la tabla trips debe coincidir con ingest_log (filas por archivo). Devuelve 0 filas si todo cuadra.
-- Requiere: tabla
-- Fuente: vista `trips` = Parquet de data/raw/{yellow,green}/*/*.parquet normalizados (scripts/taxi_common.py), o la tabla `trips` de taxi.duckdb.
-- Decision: 0 filas: trips coincide archivo por archivo con ingest_log.
SELECT l.source_file, l.n_rows AS filas_log, count(t.source_file) AS filas_trips
FROM ingest_log l LEFT JOIN trips t USING (source_file)
GROUP BY l.source_file, l.n_rows
HAVING l.n_rows <> count(t.source_file);
