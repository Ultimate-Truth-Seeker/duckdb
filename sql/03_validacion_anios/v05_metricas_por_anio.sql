-- Objetivo: comparar metricas clave entre anios para detectar cambios bruscos o inconsistencias (solo viajes plausibles).
-- Fuente: vista `trips` = Parquet de data/raw/{yellow,green}/*/*.parquet normalizados (scripts/taxi_common.py), o la tabla `trips` de taxi.duckdb.
SELECT source_year AS anio, taxi_type,
       count(*) AS viajes,
       round(avg(trip_distance), 2) AS dist_prom,
       round(avg(fare_amount), 2)   AS tarifa_prom,
       round(avg(tip_amount), 2)    AS propina_prom,
       round(avg(total_amount), 2)  AS total_prom,
       round(sum(total_amount) / 1e6, 2) AS ingresos_millones
FROM trips
WHERE trip_distance BETWEEN 0.1 AND 100 AND fare_amount BETWEEN 1 AND 500
GROUP BY ALL
ORDER BY anio, taxi_type;
