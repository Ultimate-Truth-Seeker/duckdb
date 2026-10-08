-- Objetivo: patron temporal. Viajes y total promedio por dia de la semana y hora (funciones sobre timestamp).
SELECT dayofweek(pickup_datetime) AS dia_semana, hour(pickup_datetime) AS hora,
       count(*) AS viajes, round(avg(total_amount), 2) AS total_prom
FROM trips
GROUP BY ALL
ORDER BY dia_semana, hora;
