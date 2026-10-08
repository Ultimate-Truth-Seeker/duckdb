-- Objetivo: escaneo de muchas columnas numericas (peor caso para formato columnar: se leen casi todas).
SELECT taxi_type,
       round(sum(fare_amount), 2) AS fare, round(sum(extra), 2) AS extra,
       round(sum(mta_tax), 2) AS mta, round(sum(tip_amount), 2) AS tip,
       round(sum(tolls_amount), 2) AS tolls, round(sum(improvement_surcharge), 2) AS improv,
       round(sum(congestion_surcharge), 2) AS congestion, round(sum(total_amount), 2) AS total,
       round(sum(trip_distance), 2) AS distancia
FROM trips
GROUP BY taxi_type
ORDER BY taxi_type;
