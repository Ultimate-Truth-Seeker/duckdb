-- Objetivo: zonas mas activas como origen y como destino (IDs de zona de la TLC; sin tabla de nombres en el repo).
-- Fuente: vista `trips` = Parquet de data/raw/{yellow,green}/*/*.parquet normalizados (scripts/taxi_common.py), o la tabla `trips` de taxi.duckdb.
WITH origen AS (
    SELECT pu_location_id AS zona, count(*) AS recogidas FROM trips GROUP BY zona),
destino AS (
    SELECT do_location_id AS zona, count(*) AS bajadas FROM trips GROUP BY zona)
SELECT coalesce(o.zona, d.zona) AS zona,
       coalesce(recogidas, 0) AS recogidas, coalesce(bajadas, 0) AS bajadas,
       coalesce(recogidas, 0) - coalesce(bajadas, 0) AS saldo_neto
FROM origen o FULL OUTER JOIN destino d ON o.zona = d.zona
ORDER BY recogidas DESC
LIMIT 25;
