-- Objetivo: diferencias entre taxis amarillos y verdes en una sola tabla (volumen, distancia, duracion, tarifa, propina, pasajeros, tarjeta).
-- Solo viajes plausibles: distancia 0.1-100 millas, tarifa 1-500, duracion 1-180 minutos.
-- Fuente: vista `trips` = Parquet de data/raw/{yellow,green}/*/*.parquet normalizados (scripts/taxi_common.py), o la tabla `trips` de taxi.duckdb.
WITH v AS (
    SELECT *, date_diff('second', pickup_datetime, dropoff_datetime) / 60.0 AS minutos
    FROM trips
    WHERE trip_distance BETWEEN 0.1 AND 100 AND fare_amount BETWEEN 1 AND 500
      AND dropoff_datetime > pickup_datetime)
SELECT taxi_type,
       count(*) AS viajes,
       round(avg(trip_distance), 2) AS distancia_prom_millas,
       round(avg(minutos), 1) AS duracion_prom_min,
       round(avg(fare_amount), 2) AS tarifa_prom,
       round(avg(tip_amount), 2) AS propina_prom,
       round(avg(total_amount), 2) AS total_prom,
       round(avg(passenger_count), 2) AS pasajeros_prom,
       round(100.0 * count_if(payment_type = 1) / count(*), 1) AS pct_pago_tarjeta,
       round(100.0 * count_if(pu_location_id IN (132, 138)) / count(*), 1) AS pct_recogida_aeropuertos_jfk_lga
FROM v
WHERE minutos BETWEEN 1 AND 180
GROUP BY taxi_type
ORDER BY taxi_type;
