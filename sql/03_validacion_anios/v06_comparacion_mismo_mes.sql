-- Objetivo: variacion interanual de viajes comparando el mismo mes entre anios consecutivos.
-- Fuente: vista `trips` = Parquet de data/raw/{yellow,green}/*/*.parquet normalizados (scripts/taxi_common.py), o la tabla `trips` de taxi.duckdb.
-- Decision: green baja todos los meses frente al mismo mes del anio anterior (de -7.0 % a -19.8 %); yellow sube 13-27 % en 2025 y baja 3.5-11.2 % en 2026 (feb-ago). se compara siempre el mismo mes, nunca anio completo contra 2026.
WITH m AS (
    SELECT taxi_type, source_year AS anio, source_month AS mes, count(*) AS viajes
    FROM trips GROUP BY ALL)
SELECT taxi_type, anio, mes, viajes,
       lag(viajes) OVER (PARTITION BY taxi_type, mes ORDER BY anio) AS viajes_anio_anterior,
       round(100.0 * (viajes - lag(viajes) OVER (PARTITION BY taxi_type, mes ORDER BY anio))
             / NULLIF(lag(viajes) OVER (PARTITION BY taxi_type, mes ORDER BY anio), 0), 1) AS variacion_pct
FROM m
ORDER BY taxi_type, mes, anio;
