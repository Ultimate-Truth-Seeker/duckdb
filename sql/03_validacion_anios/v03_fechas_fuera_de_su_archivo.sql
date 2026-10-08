-- Objetivo: viajes cuya fecha de recogida no corresponde al mes del archivo (error de captura o de la fuente).
-- Fuente: vista `trips` = Parquet de data/raw/{yellow,green}/*/*.parquet normalizados (scripts/taxi_common.py), o la tabla `trips` de taxi.duckdb.
-- Decision: los 64 archivos tienen entre 2 y 51 viajes fuera de su mes (algunos de 2002-2009). son pocos; se excluyen con el filtro de fechas y no se borran de trips.
SELECT source_year AS anio_archivo, source_month AS mes_archivo, taxi_type,
       count(*) AS viajes_fuera_de_mes,
       min(pickup_datetime) AS fecha_min, max(pickup_datetime) AS fecha_max
FROM trips
WHERE year(pickup_datetime) <> source_year OR month(pickup_datetime) <> source_month
GROUP BY ALL
ORDER BY viajes_fuera_de_mes DESC
LIMIT 30;
