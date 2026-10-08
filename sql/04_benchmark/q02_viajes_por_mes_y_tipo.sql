-- Objetivo: comportamiento temporal. Viajes por mes y tipo de taxi (agregacion con 2 columnas).
SELECT taxi_type, date_trunc('month', pickup_datetime) AS mes, count(*) AS viajes
FROM trips
GROUP BY ALL
ORDER BY taxi_type, mes;
