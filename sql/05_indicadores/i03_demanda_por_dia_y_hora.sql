-- Objetivo: indicador 3, patron semanal y horario. pregunta: ¿en que dias y horas se concentra la demanda? justificacion: ayuda a ubicar horas pico y valle y a diferenciar semana de fin de semana. dia_semana: 0 = domingo. suma yellow y green. visualizacion: lineas por dia con la hora en el eje x.
-- Fuente: tabla `trips` de taxi.duckdb (solo lectura) o vista `trips` sobre los Parquet de data/raw (scripts/taxi_common.py).
-- Decision: pico a las 18 h (8.64 M viajes), luego 17 h y 19 h. el jueves es el dia con mas viajes (18.9 M) y el lunes el de menos (14.8 M). conviene mirar el patron por hora y no solo por dia.
SELECT dayofweek(pickup_datetime) AS dia_semana, dayname(pickup_datetime) AS nombre_dia,
       hour(pickup_datetime) AS hora, count(*) AS viajes
FROM trips
WHERE pickup_datetime >= TIMESTAMP '2024-01-01' AND pickup_datetime < TIMESTAMP '2027-01-01'
GROUP BY ALL
ORDER BY dia_semana, hora;
