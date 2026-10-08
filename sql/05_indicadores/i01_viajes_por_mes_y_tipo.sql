-- Objetivo: indicador 1, demanda mensual. pregunta: ¿como evoluciona la demanda mes a mes y como se reparte entre yellow y green? justificacion: es la medida base del volumen del servicio y muestra estacionalidad y tendencia. visualizacion: lineas por tipo de taxi.
-- Fuente: tabla `trips` de taxi.duckdb (solo lectura) o vista `trips` sobre los Parquet de data/raw (scripts/taxi_common.py).
-- Decision: yellow va de 2.96 M viajes (ene 2024) a su maximo de 4.59 M (may 2025) y baja en 2026; green ronda 37 mil a 61 mil por mes y cae. yellow concentra casi toda la demanda; 2026 llega solo hasta agosto.
SELECT date_trunc('month', pickup_datetime)::DATE AS mes, taxi_type, count(*) AS viajes
FROM trips
WHERE pickup_datetime >= TIMESTAMP '2024-01-01' AND pickup_datetime < TIMESTAMP '2027-01-01'
GROUP BY ALL
ORDER BY mes, taxi_type;
