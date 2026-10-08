-- Objetivo: valores atipicos de tarifa con el criterio del rango intercuartil (IQR), por tipo de taxi.
-- Fuente: vista `trips` = Parquet de data/raw/{yellow,green}/*/*.parquet normalizados (scripts/taxi_common.py), o la tabla `trips` de taxi.duckdb.
WITH lim AS (
    SELECT taxi_type,
           quantile_cont(fare_amount, 0.25) AS q1,
           quantile_cont(fare_amount, 0.75) AS q3
    FROM trips WHERE fare_amount > 0
    GROUP BY taxi_type)
SELECT t.taxi_type, round(l.q1, 2) AS q1, round(l.q3, 2) AS q3,
       round(l.q3 + 1.5 * (l.q3 - l.q1), 2) AS limite_superior,
       count(*) FILTER (WHERE t.fare_amount > l.q3 + 1.5 * (l.q3 - l.q1)) AS atipicos_altos,
       round(100.0 * count(*) FILTER (WHERE t.fare_amount > l.q3 + 1.5 * (l.q3 - l.q1)) / count(*), 2) AS pct_atipicos
FROM trips t JOIN lim l USING (taxi_type)
WHERE t.fare_amount > 0
GROUP BY t.taxi_type, l.q1, l.q3
ORDER BY t.taxi_type;
