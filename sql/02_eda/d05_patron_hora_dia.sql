-- Objetivo: demanda por dia de la semana (0 = domingo) y hora; sirve para un mapa de calor.
-- Fuente: vista `trips` = Parquet de data/raw/{yellow,green}/*/*.parquet normalizados (scripts/taxi_common.py), o la tabla `trips` de taxi.duckdb.
-- Decision: yellow: pico a las 18 h (8.5 M viajes), valle de 4 a 5 h; el lunes tiene menos viajes (14.6 M) y el jueves mas (18.6 M). el filtro fijo 2024-2026 es el unico limite de la consulta.
SELECT taxi_type,
       dayofweek(pickup_datetime) AS dia_semana,
       hour(pickup_datetime) AS hora,
       count(*) AS viajes,
       round(avg(total_amount), 2) AS total_prom
FROM trips
WHERE pickup_datetime >= TIMESTAMP '2024-01-01' AND pickup_datetime < TIMESTAMP '2027-01-01'
GROUP BY ALL
ORDER BY taxi_type, dia_semana, hora;
