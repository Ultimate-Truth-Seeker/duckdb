-- Objetivo: confirmar que cada archivo mensual aporta filas (conteo por anio, mes y tipo segun el ARCHIVO de origen).
-- Fuente: vista `trips` = Parquet de data/raw/{yellow,green}/*/*.parquet normalizados (scripts/taxi_common.py), o la tabla `trips` de taxi.duckdb.
-- Decision: 32 meses (12 + 12 + 8): en todos hay filas de yellow y de green, ningun mes queda en cero.
SELECT source_year AS anio, source_month AS mes,
       count(*) FILTER (WHERE taxi_type = 'yellow') AS yellow,
       count(*) FILTER (WHERE taxi_type = 'green')  AS green,
       count(*) AS total
FROM trips
GROUP BY ALL
ORDER BY anio, mes;
