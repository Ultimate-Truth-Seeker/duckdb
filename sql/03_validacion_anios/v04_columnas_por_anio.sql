-- Objetivo: % de filas NO nulas de las columnas que cambian entre anios (esquema evolutivo).
-- cbd_congestion_fee aparece desde 2025; airport_fee solo en yellow; ehail_fee/trip_type solo en green.
-- Fuente: vista `trips` = Parquet de data/raw/{yellow,green}/*/*.parquet normalizados (scripts/taxi_common.py), o la tabla `trips` de taxi.duckdb.
SELECT source_year AS anio, taxi_type, count(*) AS filas,
       round(100.0 * count(cbd_congestion_fee) / count(*), 1) AS pct_cbd_congestion_fee,
       round(100.0 * count(airport_fee) / count(*), 1)        AS pct_airport_fee,
       round(100.0 * count(congestion_surcharge) / count(*), 1) AS pct_congestion_surcharge,
       round(100.0 * count(ehail_fee) / count(*), 1)          AS pct_ehail_fee,
       round(100.0 * count(trip_type) / count(*), 1)          AS pct_trip_type
FROM trips
GROUP BY ALL
ORDER BY anio, taxi_type;
