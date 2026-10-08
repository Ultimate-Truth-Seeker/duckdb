-- Objetivo: duracion y velocidad promedio, usando solo viajes plausibles (1 min a 3 h, distancia > 0).
-- Fuente: vista `trips` = Parquet de data/raw/{yellow,green}/*/*.parquet normalizados (scripts/taxi_common.py), o la tabla `trips` de taxi.duckdb.
WITH v AS (
    SELECT taxi_type, trip_distance,
           date_diff('second', pickup_datetime, dropoff_datetime) / 60.0 AS minutos
    FROM trips
    WHERE dropoff_datetime > pickup_datetime AND trip_distance > 0
)
SELECT taxi_type, count(*) AS viajes,
       round(avg(minutos), 1) AS duracion_prom_min,
       round(median(minutos), 1) AS duracion_mediana_min,
       round(quantile_cont(minutos, 0.95), 1) AS duracion_p95_min,
       round(sum(trip_distance) / (sum(minutos) / 60.0), 1) AS velocidad_prom_mph
FROM v
WHERE minutos BETWEEN 1 AND 180
GROUP BY taxi_type
ORDER BY taxi_type;
