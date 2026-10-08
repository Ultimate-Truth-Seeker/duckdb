-- Objetivo: caracteristicas de los viajes. Las 20 zonas de recogida con mas viajes (GROUP BY + TOP-N).
SELECT pu_location_id, count(*) AS viajes, round(avg(trip_distance), 2) AS distancia_prom
FROM trips
GROUP BY pu_location_id
ORDER BY viajes DESC, pu_location_id
LIMIT 20;
