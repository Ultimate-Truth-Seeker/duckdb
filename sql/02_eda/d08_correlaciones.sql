-- Objetivo: correlacion entre variables numericas (viajes con valores positivos y plausibles).
-- Fuente: vista `trips` = Parquet de data/raw/{yellow,green}/*/*.parquet normalizados (scripts/taxi_common.py), o la tabla `trips` de taxi.duckdb.
-- Decision: distancia y tarifa se correlacionan fuerte en yellow (0.91) y menos en green (0.74); pasajeros casi no influye (0.03-0.06). la distancia es el mejor predictor de ingreso.
SELECT taxi_type,
       round(corr(trip_distance, fare_amount), 3) AS corr_distancia_tarifa,
       round(corr(trip_distance, total_amount), 3) AS corr_distancia_total,
       round(corr(fare_amount, tip_amount), 3)     AS corr_tarifa_propina,
       round(corr(passenger_count, total_amount), 3) AS corr_pasajeros_total
FROM trips
WHERE trip_distance BETWEEN 0.1 AND 100 AND fare_amount BETWEEN 1 AND 500
GROUP BY taxi_type
ORDER BY taxi_type;
