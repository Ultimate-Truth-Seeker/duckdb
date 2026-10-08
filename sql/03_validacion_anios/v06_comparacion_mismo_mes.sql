-- Objetivo: variacion interanual de viajes comparando el mismo mes entre anios consecutivos.
-- Fuente: vista `trips` = Parquet de data/raw/{yellow,green}/*/*.parquet normalizados (scripts/taxi_common.py), o la tabla `trips` de taxi.duckdb.
WITH m AS (
    SELECT taxi_type, source_year AS anio, source_month AS mes, count(*) AS viajes
    FROM trips GROUP BY ALL)
SELECT taxi_type, anio, mes, viajes,
       lag(viajes) OVER (PARTITION BY taxi_type, mes ORDER BY anio) AS viajes_anio_anterior,
       round(100.0 * (viajes - lag(viajes) OVER (PARTITION BY taxi_type, mes ORDER BY anio))
             / NULLIF(lag(viajes) OVER (PARTITION BY taxi_type, mes ORDER BY anio), 0), 1) AS variacion_pct
FROM m
ORDER BY taxi_type, mes, anio;
