-- Objetivo: indicador 5, zonas de recogida. pregunta: ¿que zonas concentran mas recogidas? justificacion: la zona es la unica variable espacial del conjunto y orienta donde esta la demanda. se muestran ids de zona porque el repositorio no incluye la tabla de nombres. visualizacion: barras horizontales del top 10.
-- Fuente: tabla `trips` de taxi.duckdb (solo lectura) o vista `trips` sobre los Parquet de data/raw (scripts/taxi_common.py).
-- Decision: las zonas 237, 132 y 161 concentran ~4.3-4.4 % de las recogidas cada una; el top 10 suma 34.8 % de los viajes. son ids: para ponerles nombre falta la tabla de zonas de la tlc.
SELECT pu_location_id AS zona, count(*) AS viajes,
       round(100.0 * count(*) / sum(count(*)) OVER (), 2) AS pct_viajes
FROM trips
WHERE pickup_datetime >= TIMESTAMP '2024-01-01' AND pickup_datetime < TIMESTAMP '2027-01-01'
  AND pu_location_id BETWEEN 1 AND 265
GROUP BY pu_location_id
ORDER BY viajes DESC
LIMIT 10;
