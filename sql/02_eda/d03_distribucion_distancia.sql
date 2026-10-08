-- Objetivo: histograma de distancia de viaje (millas) para ver forma de la distribucion y cola larga.
-- Fuente: vista `trips` = Parquet de data/raw/{yellow,green}/*/*.parquet normalizados (scripts/taxi_common.py), o la tabla `trips` de taxi.duckdb.
-- Decision: la mayoria de viajes es corta: ~47 % de yellow y 51 % de green estan entre 1 y 3 millas; <= 0 millas son 2.6 % (yellow) y 4.5 % (green). se filtra distancia > 0.1.
WITH r AS (
    SELECT taxi_type,
           CASE WHEN trip_distance <= 0 THEN '0. <= 0'
                WHEN trip_distance < 1 THEN '1. (0,1)'
                WHEN trip_distance < 3 THEN '2. [1,3)'
                WHEN trip_distance < 5 THEN '3. [3,5)'
                WHEN trip_distance < 10 THEN '4. [5,10)'
                WHEN trip_distance < 30 THEN '5. [10,30)'
                ELSE '6. >= 30' END AS rango_millas
    FROM trips
    WHERE trip_distance IS NOT NULL),
c AS (SELECT taxi_type, rango_millas, count(*) AS viajes FROM r GROUP BY ALL)
SELECT taxi_type, rango_millas, viajes,
       round(100.0 * viajes / sum(viajes) OVER (PARTITION BY taxi_type), 2) AS porcentaje
FROM c
ORDER BY taxi_type, rango_millas;
