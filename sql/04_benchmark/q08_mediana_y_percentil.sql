-- Objetivo: distribucion de valores. Mediana del total y percentil 95 de la distancia (agregados que requieren ordenar).
SELECT taxi_type,
       median(total_amount) AS mediana_total,
       quantile_cont(trip_distance, 0.95) AS p95_distancia
FROM trips
WHERE trip_distance > 0
GROUP BY taxi_type
ORDER BY taxi_type;
