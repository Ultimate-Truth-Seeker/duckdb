-- Objetivo: indicador 7, variacion interanual. pregunta: ¿crece o cae la demanda frente al mismo mes del anio anterior? justificacion: comparar el mismo mes elimina la estacionalidad y no mezcla un 2026 incompleto con anios completos. visualizacion: barras de variacion porcentual por mes y tipo.
-- Fuente: tabla `trips` de taxi.duckdb (solo lectura) o vista `trips` sobre los Parquet de data/raw (scripts/taxi_common.py).
-- Decision: green cae todos los meses (de -7.0 % a -14.6 % en 2025 y de -10.6 % a -19.8 % en 2026); yellow sube de +13.0 % a +26.7 % en 2025 y en 2026 va de -11.2 % a +7.2 %. se compara siempre el mismo mes.
WITH m AS (
    SELECT taxi_type, date_trunc('month', pickup_datetime)::DATE AS mes, count(*) AS viajes
    FROM trips
    WHERE pickup_datetime >= TIMESTAMP '2024-01-01' AND pickup_datetime < TIMESTAMP '2027-01-01'
    GROUP BY ALL),
c AS (
    SELECT *, lag(viajes) OVER (PARTITION BY taxi_type, month(mes) ORDER BY mes) AS viajes_anio_anterior
    FROM m)
SELECT taxi_type, mes, viajes, viajes_anio_anterior,
       round(100.0 * (viajes - viajes_anio_anterior) / viajes_anio_anterior, 1) AS variacion_pct
FROM c
WHERE viajes_anio_anterior IS NOT NULL
ORDER BY taxi_type, mes;
