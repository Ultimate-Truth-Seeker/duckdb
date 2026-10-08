-- Objetivo: variables de pago. Promedios de tarifa, propina y total por tipo de taxi y metodo de pago.
SELECT taxi_type, payment_type,
       count(*) AS viajes,
       round(avg(fare_amount), 2) AS tarifa_prom,
       round(avg(tip_amount), 2) AS propina_prom,
       round(avg(total_amount), 2) AS total_prom
FROM trips
GROUP BY ALL
ORDER BY taxi_type, payment_type;
