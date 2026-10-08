-- Objetivo: comportamiento temporal. Viajes e ingresos por mes de recogida y tipo de taxi (tendencia y estacionalidad).
-- Fuente: vista `trips` = Parquet de data/raw/{yellow,green}/*/*.parquet normalizados (scripts/taxi_common.py), o la tabla `trips` de taxi.duckdb.
SELECT taxi_type, date_trunc('month', pickup_datetime) AS mes,
       count(*) AS viajes,
       round(sum(total_amount), 0) AS ingresos,
       round(avg(total_amount), 2) AS total_prom
FROM trips
WHERE pickup_datetime >= TIMESTAMP '2024-01-01' AND pickup_datetime < TIMESTAMP '2027-01-01'
  AND total_amount BETWEEN 0 AND 1000
GROUP BY ALL
ORDER BY taxi_type, mes;
