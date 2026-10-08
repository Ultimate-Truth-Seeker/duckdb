-- Objetivo: metodo de pago y propinas. La propina solo se registra de forma confiable con tarjeta (payment_type = 1).
-- Fuente: vista `trips` = Parquet de data/raw/{yellow,green}/*/*.parquet normalizados (scripts/taxi_common.py), o la tabla `trips` de taxi.duckdb.
-- Decision: tarjeta es ~67 % de los viajes con propina media 4.33 (yellow) y efectivo 0.00: la propina en efectivo no se registra. en yellow, payment_type 0 (19.6 %) coincide con los nulos de passenger_count; analizar propinas solo con tarjeta.
WITH p AS (
    SELECT taxi_type, payment_type, count(*) AS viajes,
           round(avg(tip_amount), 2) AS propina_prom,
           round(avg(100.0 * tip_amount / fare_amount) FILTER (WHERE fare_amount > 0), 2) AS propina_pct_tarifa
    FROM trips
    GROUP BY ALL)
SELECT taxi_type, payment_type, viajes,
       round(100.0 * viajes / sum(viajes) OVER (PARTITION BY taxi_type), 2) AS pct_viajes,
       propina_prom, propina_pct_tarifa
FROM p
ORDER BY taxi_type, payment_type;
