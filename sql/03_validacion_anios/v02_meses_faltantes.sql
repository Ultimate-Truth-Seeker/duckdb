-- Objetivo: detectar meses sin archivo entre el primero y el ultimo cargado, por tipo de taxi.
-- Un mes final ausente puede ser normal (la TLC publica con atraso); un hueco intermedio no.
-- Fuente: vista `trips` = Parquet de data/raw/{yellow,green}/*/*.parquet normalizados (scripts/taxi_common.py), o la tabla `trips` de taxi.duckdb.
WITH rango AS (
    SELECT taxi_type,
           min(mes) AS desde, max(mes) AS hasta
    FROM (SELECT DISTINCT taxi_type, make_date(source_year, source_month, 1) AS mes FROM trips)
    GROUP BY taxi_type),
esperados AS (
    SELECT r.taxi_type, CAST(m.generate_series AS DATE) AS mes
    FROM rango r, generate_series(r.desde, r.hasta, INTERVAL 1 MONTH) AS m),
presentes AS (
    SELECT DISTINCT taxi_type, make_date(source_year, source_month, 1) AS mes FROM trips)
SELECT e.taxi_type, e.mes AS mes_faltante
FROM esperados e ANTI JOIN presentes p USING (taxi_type, mes)
ORDER BY 1, 2;
