-- Objetivo: valores atipicos. Filtro muy selectivo (pocas filas cumplen); favorece pruning y estadisticas por columna.
SELECT taxi_type, count(*) AS viajes_atipicos
FROM trips
WHERE trip_distance > 100 OR total_amount > 500 OR fare_amount < 0
GROUP BY taxi_type
ORDER BY taxi_type;
