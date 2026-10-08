-- Objetivo: indicador 4, forma de pago y propina. pregunta: ¿como pagan los pasajeros y cuanta propina dejan segun el pago? justificacion: la propina solo se registra con tarjeta, asi que separar por tipo de pago evita conclusiones falsas. se usan viajes con tarifa entre 1 y 500. visualizacion: barras del porcentaje de viajes y tabla con la propina media.
-- Fuente: tabla `trips` de taxi.duckdb (solo lectura) o vista `trips` sobre los Parquet de data/raw (scripts/taxi_common.py).
-- Decision: yellow: 69.6 % paga con tarjeta (propina media 4.33), 10.8 % en efectivo (0.00) y 18.2 % queda como 'otro o sin dato'. green: 68.6 % tarjeta (3.66) y 23.5 % efectivo. la propina de efectivo no se registra, no es que no haya.
WITH p AS (
    SELECT taxi_type,
           CASE payment_type WHEN 1 THEN 'tarjeta' WHEN 2 THEN 'efectivo'
                             WHEN 3 THEN 'sin cargo' WHEN 4 THEN 'disputa'
                             ELSE 'otro o sin dato' END AS tipo_pago,
           count(*) AS viajes,
           round(avg(tip_amount), 2) AS propina_media
    FROM trips
    WHERE pickup_datetime >= TIMESTAMP '2024-01-01' AND pickup_datetime < TIMESTAMP '2027-01-01'
      AND fare_amount BETWEEN 1 AND 500
    GROUP BY ALL)
SELECT taxi_type, tipo_pago, viajes,
       round(100.0 * viajes / sum(viajes) OVER (PARTITION BY taxi_type), 2) AS pct_viajes,
       propina_media
FROM p
ORDER BY taxi_type, viajes DESC;
