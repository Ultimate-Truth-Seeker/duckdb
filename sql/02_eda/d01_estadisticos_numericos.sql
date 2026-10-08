-- Objetivo: estadisticos descriptivos de las variables numericas clave por tipo de taxi.
-- Fuente: vista `trips` = Parquet de data/raw/{yellow,green}/*/*.parquet normalizados (scripts/taxi_common.py), o la tabla `trips` de taxi.duckdb.
SELECT taxi_type,
       count(*) AS n,
       round(avg(trip_distance), 2) AS dist_prom, round(median(trip_distance), 2) AS dist_mediana,
       round(quantile_cont(trip_distance, 0.99), 2) AS dist_p99, max(trip_distance) AS dist_max,
       round(avg(fare_amount), 2) AS tarifa_prom, round(median(fare_amount), 2) AS tarifa_mediana,
       round(quantile_cont(fare_amount, 0.99), 2) AS tarifa_p99, max(fare_amount) AS tarifa_max,
       round(avg(total_amount), 2) AS total_prom, round(stddev(total_amount), 2) AS total_desv
FROM trips
GROUP BY taxi_type
ORDER BY taxi_type;
