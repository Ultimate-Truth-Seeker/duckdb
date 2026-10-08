-- Objetivo: cuantificar problemas de calidad (registros sospechosos) por tipo de taxi.
-- Fuente: vista `trips` = Parquet de data/raw/{yellow,green}/*/*.parquet normalizados (scripts/taxi_common.py), o la tabla `trips` de taxi.duckdb.
SELECT taxi_type, count(*) AS viajes,
       count_if(dropoff_datetime < pickup_datetime)                    AS bajada_antes_de_recogida,
       count_if(dropoff_datetime - pickup_datetime > INTERVAL 24 HOUR) AS duracion_mayor_24h,
       count_if(trip_distance <= 0)                                    AS distancia_cero_o_negativa,
       count_if(fare_amount <= 0)                                      AS tarifa_cero_o_negativa,
       count_if(total_amount < 0)                                      AS total_negativo,
       count_if(passenger_count IS NULL OR passenger_count = 0)        AS pasajeros_nulo_o_cero,
       count_if(pu_location_id IS NULL OR pu_location_id NOT BETWEEN 1 AND 265) AS zona_recogida_invalida,
       count_if(pickup_datetime < TIMESTAMP '2024-01-01'
                OR pickup_datetime >= TIMESTAMP '2027-01-01')          AS fecha_fuera_de_2024_2026
FROM trips
GROUP BY taxi_type
ORDER BY taxi_type;
