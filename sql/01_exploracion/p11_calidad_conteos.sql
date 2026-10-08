-- Objetivo: 3.6 cuantificar registros problematicos por tipo de taxi (fechas, duraciones, distancias, tarifas, pasajeros, zonas).
-- Fuente: /workspace/data/raw/yellow/*/*.parquet y /workspace/data/raw/green/*/*.parquet
-- Decision: yellow: 3.8 M tarifas <= 0, 3.1 M distancias <= 0, 1.7 M totales negativos, 24 M pasajeros nulo/0 (20 %). se filtra en cada consulta (distancia 0.1-100, tarifa 1-500, duracion 1-180 min); trips queda sin corregir.
WITH v AS (
    SELECT 'yellow' AS tipo, tpep_pickup_datetime AS recogida, tpep_dropoff_datetime AS bajada, passenger_count,
           trip_distance, fare_amount, total_amount, PULocationID, filename
    FROM read_parquet('/workspace/data/raw/yellow/*/*.parquet', union_by_name = true, filename = true)
    UNION ALL
    SELECT 'green', lpep_pickup_datetime, lpep_dropoff_datetime, passenger_count,
           trip_distance, fare_amount, total_amount, PULocationID, filename
    FROM read_parquet('/workspace/data/raw/green/*/*.parquet', union_by_name = true, filename = true))
SELECT tipo, count(*) AS registros,
       count_if(year(recogida) <> CAST(regexp_extract(filename, '(\d{4})-\d{2}\.parquet', 1) AS INTEGER)) AS recogida_fuera_del_anio_del_archivo,
       count_if(bajada < recogida)                                    AS bajada_antes_de_recogida,
       count_if(bajada - recogida > INTERVAL 24 HOUR)                 AS duracion_mayor_24h,
       count_if(trip_distance <= 0)                                   AS distancia_cero_o_negativa,
       count_if(trip_distance > 100)                                  AS distancia_mayor_100_millas,
       count_if(fare_amount <= 0)                                     AS tarifa_cero_o_negativa,
       count_if(total_amount < 0)                                     AS total_negativo,
       count_if(passenger_count IS NULL OR passenger_count = 0)       AS pasajeros_nulo_o_cero,
       count_if(PULocationID IS NULL OR PULocationID NOT BETWEEN 1 AND 265) AS zona_recogida_invalida
FROM v
GROUP BY tipo
ORDER BY tipo;
