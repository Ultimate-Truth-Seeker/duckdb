-- Objetivo: indicador 2, ingresos mensuales. pregunta: ¿cuanto dinero generan los viajes cada mes y que tipo de taxi aporta mas? justificacion: el volumen no basta, el ingreso mezcla viajes y tarifa. se usa total_amount entre 0 y 1000 (como d10) para no sumar montos imposibles. visualizacion: barras apiladas por tipo.
-- Fuente: tabla `trips` de taxi.duckdb (solo lectura) o vista `trips` sobre los Parquet de data/raw (scripts/taxi_common.py).
-- Decision: yellow genera ~99 % del ingreso: 1,162 M (2024), 1,334 M (2025) y 898 M (2026 hasta agosto); green 16.0 M, 14.9 M y 8.6 M. el ingreso sigue la forma del volumen, con un salto de 2024 a 2025 en yellow.
SELECT date_trunc('month', pickup_datetime)::DATE AS mes, taxi_type,
       round(sum(total_amount) / 1e6, 2) AS ingresos_millones
FROM trips
WHERE pickup_datetime >= TIMESTAMP '2024-01-01' AND pickup_datetime < TIMESTAMP '2027-01-01'
  AND total_amount BETWEEN 0 AND 1000
GROUP BY ALL
ORDER BY mes, taxi_type;
