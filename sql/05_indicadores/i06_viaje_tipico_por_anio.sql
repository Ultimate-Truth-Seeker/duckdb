-- Objetivo: indicador 6, viaje tipico. pregunta: ¿como es un viaje tipico y cambia de un anio a otro? justificacion: los promedios estan distorsionados por valores imposibles (d01), por eso se usa la mediana sobre viajes plausibles (distancia 0.1-100 millas, tarifa 1-500, duracion 1-180 min). 2026 llega hasta agosto. visualizacion: tabla y barras agrupadas por anio y tipo.
-- Fuente: tabla `trips` de taxi.duckdb (solo lectura) o vista `trips` sobre los Parquet de data/raw (scripts/taxi_common.py).
-- Decision: el viaje tipico se alarga poco a poco: yellow pasa de 1.80 a 1.95 millas y de 13.1 a 14.1 min (2024 a 2026); green de 1.99 a 2.15 millas y de 12.1 a 13.3 min. la tarifa mediana de yellow sube de 14.20 a 15.60 solo en 2026; la de green se mantiene en 13.50.
WITH v AS (
    SELECT taxi_type, year(pickup_datetime) AS anio, trip_distance, fare_amount,
           date_diff('second', pickup_datetime, dropoff_datetime) / 60.0 AS minutos
    FROM trips
    WHERE pickup_datetime >= TIMESTAMP '2024-01-01' AND pickup_datetime < TIMESTAMP '2027-01-01'
      AND dropoff_datetime > pickup_datetime
      AND trip_distance BETWEEN 0.1 AND 100
      AND fare_amount BETWEEN 1 AND 500)
SELECT taxi_type, anio, count(*) AS viajes,
       round(median(trip_distance), 2) AS distancia_mediana_millas,
       round(median(minutos), 1) AS duracion_mediana_min,
       round(median(fare_amount), 2) AS tarifa_mediana
FROM v
WHERE minutos BETWEEN 1 AND 180
GROUP BY taxi_type, anio
ORDER BY taxi_type, anio;
