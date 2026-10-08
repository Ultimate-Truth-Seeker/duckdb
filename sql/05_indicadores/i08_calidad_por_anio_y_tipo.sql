-- Objetivo: indicador 8, calidad de datos. pregunta: ¿que proporcion de los registros es inconsistente y mejora o empeora por anio? justificacion: cualquier indicador depende de la calidad del dato; mide cuanto se descarta con los filtros del analisis. se agrupa por anio del archivo (source_year). visualizacion: barras por anio y tipo.
-- Fuente: tabla `trips` de taxi.duckdb (solo lectura) o vista `trips` sobre los Parquet de data/raw (scripts/taxi_common.py).
-- Decision: yellow 2025 tiene 9.58 % de registros inconsistentes contra 3.71 % en 2024 y 5.00 % en 2026, por tarifas negativas (2.85 M, el 5.8 % del anio; 72 % de las tarifas < 1 de ese anio son de payment_type 0). green se mantiene entre 5.5 % y 6.0 %. no se corrige trips: se filtra en cada indicador.
SELECT taxi_type, source_year AS anio, count(*) AS viajes,
       round(100.0 * count_if(trip_distance <= 0 OR trip_distance > 100) / count(*), 2) AS pct_distancia_invalida,
       round(100.0 * count_if(fare_amount < 1 OR fare_amount > 500) / count(*), 2) AS pct_tarifa_invalida,
       round(100.0 * count_if(dropoff_datetime <= pickup_datetime
                              OR dropoff_datetime - pickup_datetime > INTERVAL 3 HOUR) / count(*), 2) AS pct_duracion_invalida,
       round(100.0 * count_if(trip_distance <= 0 OR trip_distance > 100
                              OR fare_amount < 1 OR fare_amount > 500
                              OR dropoff_datetime <= pickup_datetime
                              OR dropoff_datetime - pickup_datetime > INTERVAL 3 HOUR) / count(*), 2) AS pct_alguna
FROM trips
GROUP BY taxi_type, source_year
ORDER BY taxi_type, anio;
