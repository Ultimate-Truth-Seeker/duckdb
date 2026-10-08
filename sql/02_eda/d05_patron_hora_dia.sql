-- Objetivo: demanda por dia de la semana (0 = domingo) y hora; sirve para un mapa de calor.
-- Fuente: vista `trips` = Parquet de data/raw/{yellow,green}/*/*.parquet normalizados (scripts/taxi_common.py), o la tabla `trips` de taxi.duckdb.
SELECT taxi_type,
       dayofweek(pickup_datetime) AS dia_semana,
       hour(pickup_datetime) AS hora,
       count(*) AS viajes,
       round(avg(total_amount), 2) AS total_prom
FROM trips
WHERE pickup_datetime >= TIMESTAMP '2024-01-01' AND pickup_datetime < TIMESTAMP '2027-01-01'
GROUP BY ALL
ORDER BY taxi_type, dia_semana, hora;
