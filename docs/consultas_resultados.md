# Consultas documentadas con su resultado

Generado por `scripts/document_queries.py` el 2026-10-09 02:39. Fuente de datos: **tabla** (64 archivos Parquet en `data/raw`). No editar a mano: la decision de cada consulta se escribe en su `.sql` (`-- Decision:`) y se regenera este archivo.

## Resumen de ejecucion

| Consulta | Estado | Filas | Segundos |
|---|---|---|---|
| sql/01_exploracion/p01_archivos.sql | OK | 9 | 0.09 |
| sql/01_exploracion/p02_registros.sql | OK | 9 | 0.27 |
| sql/01_exploracion/p03_columnas_tipos_yellow.sql | OK | 21 | 0.06 |
| sql/01_exploracion/p04_columnas_tipos_green.sql | OK | 22 | 0.06 |
| sql/01_exploracion/p05_comparar_columnas.sql | OK | 25 | 0.12 |
| sql/01_exploracion/p06_cambios_de_tipo_entre_archivos.sql | OK | 0 | 0.10 |
| sql/01_exploracion/p07_columnas_por_archivo.sql | OK | 4 | 0.10 |
| sql/01_exploracion/p08_muestra.sql | OK | 10 | 0.56 |
| sql/01_exploracion/p09_resumen_yellow.sql | OK | 21 | 37.64 |
| sql/01_exploracion/p10_resumen_green.sql | OK | 22 | 0.81 |
| sql/01_exploracion/p11_calidad_conteos.sql | OK | 2 | 5.77 |
| sql/01_exploracion/p12_fechas_fuera_de_rango.sql | OK | 15 | 1.38 |
| sql/02_eda/d01_estadisticos_numericos.sql | OK | 2 | 46.84 |
| sql/02_eda/d02_calidad_datos.sql | OK | 2 | 5.52 |
| sql/02_eda/d03_distribucion_distancia.sql | OK | 14 | 1.36 |
| sql/02_eda/d04_duracion_y_velocidad.sql | OK | 2 | 10.20 |
| sql/02_eda/d05_patron_hora_dia.sql | OK | 336 | 0.51 |
| sql/02_eda/d06_pago_y_propinas.sql | OK | 12 | 1.79 |
| sql/02_eda/d07_zonas_recogida_destino.sql | OK | 25 | 1.16 |
| sql/02_eda/d08_correlaciones.sql | OK | 2 | 0.83 |
| sql/02_eda/d09_atipicos_iqr.sql | OK | 2 | 11.97 |
| sql/02_eda/d10_tendencia_mensual.sql | OK | 64 | 0.94 |
| sql/02_eda/d11_comparacion_yellow_green.sql | OK | 2 | 1.39 |
| sql/03_validacion_anios/v00_consulta_conjunta_parquet.sql | OK | 6 | 2.11 |
| sql/03_validacion_anios/v01_viajes_por_anio_mes.sql | OK | 32 | 0.23 |
| sql/03_validacion_anios/v02_meses_faltantes.sql | OK | 0 | 0.19 |
| sql/03_validacion_anios/v03_fechas_fuera_de_su_archivo.sql | OK | 30 | 0.14 |
| sql/03_validacion_anios/v04_columnas_por_anio.sql | OK | 6 | 1.26 |
| sql/03_validacion_anios/v05_metricas_por_anio.sql | OK | 6 | 0.64 |
| sql/03_validacion_anios/v06_comparacion_mismo_mes.sql | OK | 64 | 0.19 |
| sql/03_validacion_anios/v07_filas_vs_ingest_log.sql | OK | 0 | 0.64 |
| sql/03_validacion_anios/v08_filas_vs_parquet.sql | OK | 0 | 0.13 |
| sql/05_indicadores/i01_viajes_por_mes_y_tipo.sql | OK | 64 | 0.65 |
| sql/05_indicadores/i02_ingresos_por_mes_y_tipo.sql | OK | 64 | 0.83 |
| sql/05_indicadores/i03_demanda_por_dia_y_hora.sql | OK | 168 | 0.53 |
| sql/05_indicadores/i04_pago_y_propina.sql | OK | 10 | 1.08 |
| sql/05_indicadores/i05_top_zonas_recogida.sql | OK | 10 | 0.07 |
| sql/05_indicadores/i06_viaje_tipico_por_anio.sql | OK | 6 | 28.51 |
| sql/05_indicadores/i07_variacion_interanual.sql | OK | 40 | 11.62 |
| sql/05_indicadores/i08_calidad_por_anio_y_tipo.sql | OK | 6 | 3.85 |

## Exploracion con Parquet directo (Ej. 3)

### `sql/01_exploracion/p01_archivos.sql`

**Objetivo:** 3.1 cantidad de archivos Parquet disponibles, por tipo de taxi y anio (con subtotales y total).

**Fuente:** /workspace/data/raw/*/*/*.parquet

**Consulta SQL:**

```sql
-- Objetivo: 3.1 cantidad de archivos Parquet disponibles, por tipo de taxi y anio (con subtotales y total).
-- Fuente: /workspace/data/raw/*/*/*.parquet
-- Decision: 64 archivos (32 por tipo): 12 meses de 2024 y 2025 y 8 de 2026. el resto de 2026 aun no esta publicado, asi que 2026 se trata como incompleto.
SELECT regexp_extract(file, 'raw/([^/]+)/', 1) AS tipo,
       regexp_extract(file, '/(\d{4})/', 1)    AS anio,
       count(*) AS archivos
FROM glob('/workspace/data/raw/*/*/*.parquet')
GROUP BY ROLLUP (tipo, anio)
ORDER BY tipo NULLS LAST, anio NULLS LAST;
```

**Resultado** (9 filas; se muestran 9; 0.09 s):

| tipo | anio | archivos |
|---|---|---|
| green | 2024 | 12 |
| green | 2025 | 12 |
| green | 2026 | 8 |
| green |  | 32 |
| yellow | 2024 | 12 |
| yellow | 2025 | 12 |
| yellow | 2026 | 8 |
| yellow |  | 32 |
|  |  | 64 |

**Decision / interpretacion:** 64 archivos (32 por tipo): 12 meses de 2024 y 2025 y 8 de 2026. el resto de 2026 aun no esta publicado, asi que 2026 se trata como incompleto.

### `sql/01_exploracion/p02_registros.sql`

**Objetivo:** 3.2 cantidad de registros disponibles, por tipo de taxi y anio de archivo (con subtotales y total).

**Fuente:** /workspace/data/raw/*/*/*.parquet

**Consulta SQL:**

```sql
-- Objetivo: 3.2 cantidad de registros disponibles, por tipo de taxi y anio de archivo (con subtotales y total).
-- Fuente: /workspace/data/raw/*/*/*.parquet
-- Decision: 121,184,384 viajes (yellow 119.6 M, green 1.59 M). coincide con verify_data.py y con la tabla trips. yellow es ~75 veces mas grande que green.
SELECT regexp_extract(filename, 'raw/([^/]+)/', 1) AS tipo,
       regexp_extract(filename, '/(\d{4})/', 1)    AS anio,
       count(*) AS registros
FROM read_parquet('/workspace/data/raw/*/*/*.parquet', union_by_name = true, filename = true)
GROUP BY ROLLUP (tipo, anio)
ORDER BY tipo NULLS LAST, anio NULLS LAST;
```

**Resultado** (9 filas; se muestran 9; 0.27 s):

| tipo | anio | registros |
|---|---|---|
| green | 2024 | 660,218 |
| green | 2025 | 591,375 |
| green | 2026 | 337,114 |
| green |  | 1,588,707 |
| yellow | 2024 | 41,169,720 |
| yellow | 2025 | 48,722,602 |
| yellow | 2026 | 29,703,355 |
| yellow |  | 119,595,677 |
|  |  | 121,184,384 |

**Decision / interpretacion:** 121,184,384 viajes (yellow 119.6 M, green 1.59 M). coincide con verify_data.py y con la tabla trips. yellow es ~75 veces mas grande que green.

### `sql/01_exploracion/p03_columnas_tipos_yellow.sql`

**Objetivo:** 3.3 y 3.4 columnas y tipos de datos de los archivos de taxis amarillos (esquema unificado de todos los archivos).

**Fuente:** /workspace/data/raw/yellow/*/*.parquet

**Consulta SQL:**

```sql
-- Objetivo: 3.3 y 3.4 columnas y tipos de datos de los archivos de taxis amarillos (esquema unificado de todos los archivos).
-- Fuente: /workspace/data/raw/yellow/*/*.parquet
-- Decision: 21 columnas en yellow. nombres con mayusculas mezcladas (VendorID, Airport_fee) y prefijo tpep_; se normalizan a minusculas en taxi_common.py.
DESCRIBE SELECT * FROM read_parquet('/workspace/data/raw/yellow/*/*.parquet', union_by_name = true);
```

**Resultado** (21 filas; se muestran 15; 0.06 s):

| column_name | column_type | null | key | default | extra |
|---|---|---|---|---|---|
| VendorID | INTEGER | YES |  |  |  |
| tpep_pickup_datetime | TIMESTAMP | YES |  |  |  |
| tpep_dropoff_datetime | TIMESTAMP | YES |  |  |  |
| passenger_count | BIGINT | YES |  |  |  |
| trip_distance | DOUBLE | YES |  |  |  |
| RatecodeID | BIGINT | YES |  |  |  |
| store_and_fwd_flag | VARCHAR | YES |  |  |  |
| PULocationID | INTEGER | YES |  |  |  |
| DOLocationID | INTEGER | YES |  |  |  |
| payment_type | BIGINT | YES |  |  |  |
| fare_amount | DOUBLE | YES |  |  |  |
| extra | DOUBLE | YES |  |  |  |
| mta_tax | DOUBLE | YES |  |  |  |
| tip_amount | DOUBLE | YES |  |  |  |
| tolls_amount | DOUBLE | YES |  |  |  |

**Decision / interpretacion:** 21 columnas en yellow. nombres con mayusculas mezcladas (VendorID, Airport_fee) y prefijo tpep_; se normalizan a minusculas en taxi_common.py.

### `sql/01_exploracion/p04_columnas_tipos_green.sql`

**Objetivo:** 3.3 y 3.4 columnas y tipos de datos de los archivos de taxis verdes (esquema unificado de todos los archivos).

**Fuente:** /workspace/data/raw/green/*/*.parquet

**Consulta SQL:**

```sql
-- Objetivo: 3.3 y 3.4 columnas y tipos de datos de los archivos de taxis verdes (esquema unificado de todos los archivos).
-- Fuente: /workspace/data/raw/green/*/*.parquet
-- Decision: 22 columnas en green (prefijo lpep_, con trip_type y ehail_fee que yellow no tiene). se mapean al mismo esquema.
DESCRIBE SELECT * FROM read_parquet('/workspace/data/raw/green/*/*.parquet', union_by_name = true);
```

**Resultado** (22 filas; se muestran 15; 0.06 s):

| column_name | column_type | null | key | default | extra |
|---|---|---|---|---|---|
| VendorID | INTEGER | YES |  |  |  |
| lpep_pickup_datetime | TIMESTAMP | YES |  |  |  |
| lpep_dropoff_datetime | TIMESTAMP | YES |  |  |  |
| store_and_fwd_flag | VARCHAR | YES |  |  |  |
| RatecodeID | BIGINT | YES |  |  |  |
| PULocationID | INTEGER | YES |  |  |  |
| DOLocationID | INTEGER | YES |  |  |  |
| passenger_count | BIGINT | YES |  |  |  |
| trip_distance | DOUBLE | YES |  |  |  |
| fare_amount | DOUBLE | YES |  |  |  |
| extra | DOUBLE | YES |  |  |  |
| mta_tax | DOUBLE | YES |  |  |  |
| tip_amount | DOUBLE | YES |  |  |  |
| tolls_amount | DOUBLE | YES |  |  |  |
| ehail_fee | DOUBLE | YES |  |  |  |

**Decision / interpretacion:** 22 columnas en green (prefijo lpep_, con trip_type y ehail_fee que yellow no tiene). se mapean al mismo esquema.

### `sql/01_exploracion/p05_comparar_columnas.sql`

**Objetivo:** 3.3 comparar las columnas de yellow y green (cuales son comunes, cuales exclusivas y si cambia el tipo).

**Fuente:** /workspace/data/raw/yellow/*/*.parquet y /workspace/data/raw/green/*/*.parquet

**Consulta SQL:**

```sql
-- Objetivo: 3.3 comparar las columnas de yellow y green (cuales son comunes, cuales exclusivas y si cambia el tipo).
-- Fuente: /workspace/data/raw/yellow/*/*.parquet y /workspace/data/raw/green/*/*.parquet
-- Decision: 25 columnas entre ambos tipos: las que difieren son fechas (tpep/lpep) y las exclusivas de cada uno. se unifican con COALESCE y las ausentes quedan en NULL.
WITH y AS (SELECT lower(column_name) AS col, column_name AS nombre_yellow, column_type AS tipo_yellow
           FROM (DESCRIBE SELECT * FROM read_parquet('/workspace/data/raw/yellow/*/*.parquet', union_by_name = true))),
     g AS (SELECT lower(column_name) AS col, column_name AS nombre_green, column_type AS tipo_green
           FROM (DESCRIBE SELECT * FROM read_parquet('/workspace/data/raw/green/*/*.parquet', union_by_name = true)))
SELECT coalesce(y.col, g.col) AS columna, nombre_yellow, tipo_yellow, nombre_green, tipo_green,
       CASE WHEN y.col IS NULL THEN 'solo green' WHEN g.col IS NULL THEN 'solo yellow'
            WHEN tipo_yellow = tipo_green THEN 'comun' ELSE 'comun, tipo distinto' END AS situacion
FROM y FULL OUTER JOIN g ON y.col = g.col
ORDER BY situacion, columna;
```

**Resultado** (25 filas; se muestran 15; 0.12 s):

| columna | nombre_yellow | tipo_yellow | nombre_green | tipo_green | situacion |
|---|---|---|---|---|---|
| cbd_congestion_fee | cbd_congestion_fee | DOUBLE | cbd_congestion_fee | DOUBLE | comun |
| congestion_surcharge | congestion_surcharge | DOUBLE | congestion_surcharge | DOUBLE | comun |
| dolocationid | DOLocationID | INTEGER | DOLocationID | INTEGER | comun |
| extra | extra | DOUBLE | extra | DOUBLE | comun |
| fare_amount | fare_amount | DOUBLE | fare_amount | DOUBLE | comun |
| improvement_surcharge | improvement_surcharge | DOUBLE | improvement_surcharge | DOUBLE | comun |
| mta_tax | mta_tax | DOUBLE | mta_tax | DOUBLE | comun |
| passenger_count | passenger_count | BIGINT | passenger_count | BIGINT | comun |
| payment_type | payment_type | BIGINT | payment_type | BIGINT | comun |
| pulocationid | PULocationID | INTEGER | PULocationID | INTEGER | comun |
| ratecodeid | RatecodeID | BIGINT | RatecodeID | BIGINT | comun |
| request_source | request_source | VARCHAR | request_source | VARCHAR | comun |
| store_and_fwd_flag | store_and_fwd_flag | VARCHAR | store_and_fwd_flag | VARCHAR | comun |
| tip_amount | tip_amount | DOUBLE | tip_amount | DOUBLE | comun |
| tolls_amount | tolls_amount | DOUBLE | tolls_amount | DOUBLE | comun |

**Decision / interpretacion:** 25 columnas entre ambos tipos: las que difieren son fechas (tpep/lpep) y las exclusivas de cada uno. se unifican con COALESCE y las ausentes quedan en NULL.

### `sql/01_exploracion/p06_cambios_de_tipo_entre_archivos.sql`

**Objetivo:** 3.4 / 3.6 detectar columnas cuyo tipo fisico en Parquet cambia de un archivo a otro (riesgo al combinar archivos).

**Fuente:** /workspace/data/raw/*/*/*.parquet

**Consulta SQL:**

```sql
-- Objetivo: 3.4 / 3.6 detectar columnas cuyo tipo fisico en Parquet cambia de un archivo a otro (riesgo al combinar archivos).
-- Fuente: /workspace/data/raw/*/*/*.parquet
-- Decision: 0 filas: ninguna columna cambia de tipo fisico entre archivos. se deja TRY_CAST igual por seguridad, pero hoy no hay conflicto de tipos.
WITH s AS (
    SELECT regexp_extract(file_name, 'raw/([^/]+)/', 1) AS tipo, lower(name) AS columna, type AS tipo_parquet, file_name
    FROM parquet_schema('/workspace/data/raw/*/*/*.parquet')
    WHERE num_children IS NULL)
SELECT tipo, columna, list(DISTINCT tipo_parquet ORDER BY tipo_parquet) AS tipos_encontrados,
       count(DISTINCT file_name) AS archivos_con_la_columna
FROM s
GROUP BY tipo, columna
HAVING count(DISTINCT tipo_parquet) > 1
ORDER BY tipo, columna;
```

**Resultado** (0 filas; se muestran 0; 0.10 s):

| tipo | columna | tipos_encontrados | archivos_con_la_columna |
|---|---|---|---|

**Decision / interpretacion:** 0 filas: ninguna columna cambia de tipo fisico entre archivos. se deja TRY_CAST igual por seguridad, pero hoy no hay conflicto de tipos.

### `sql/01_exploracion/p07_columnas_por_archivo.sql`

**Objetivo:** 3.3 / 3.6 columnas que NO estan presentes en todos los archivos de un tipo (esquema que evoluciona entre meses/anios).

**Fuente:** /workspace/data/raw/*/*/*.parquet

**Consulta SQL:**

```sql
-- Objetivo: 3.3 / 3.6 columnas que NO estan presentes en todos los archivos de un tipo (esquema que evoluciona entre meses/anios).
-- Fuente: /workspace/data/raw/*/*/*.parquet
-- Decision: cbd_congestion_fee existe desde 2025-01 (20 de 32 archivos por tipo) y request_source solo desde 2026-06 (3 archivos). union_by_name es necesario; request_source no se incorpora a trips (no aporta al analisis).
WITH s AS (
    SELECT regexp_extract(file_name, 'raw/([^/]+)/', 1) AS tipo, lower(name) AS columna, file_name
    FROM parquet_schema('/workspace/data/raw/*/*/*.parquet') WHERE num_children IS NULL),
total AS (SELECT tipo, count(DISTINCT file_name) AS archivos_tipo FROM s GROUP BY tipo)
SELECT s.tipo, s.columna, count(DISTINCT s.file_name) AS archivos_con_columna, any_value(t.archivos_tipo) AS archivos_del_tipo,
       min(regexp_extract(s.file_name, '(\d{4}-\d{2})\.parquet', 1)) AS primer_mes_con_columna
FROM s JOIN total t USING (tipo)
GROUP BY s.tipo, s.columna
HAVING count(DISTINCT s.file_name) < any_value(t.archivos_tipo)
ORDER BY s.tipo, s.columna;
```

**Resultado** (4 filas; se muestran 4; 0.10 s):

| tipo | columna | archivos_con_columna | archivos_del_tipo | primer_mes_con_columna |
|---|---|---|---|---|
| green | cbd_congestion_fee | 20 | 32 | 2025-01 |
| green | request_source | 3 | 32 | 2026-06 |
| yellow | cbd_congestion_fee | 20 | 32 | 2025-01 |
| yellow | request_source | 3 | 32 | 2026-06 |

**Decision / interpretacion:** cbd_congestion_fee existe desde 2025-01 (20 de 32 archivos por tipo) y request_source solo desde 2026-06 (3 archivos). union_by_name es necesario; request_source no se incorpora a trips (no aporta al analisis).

### `sql/01_exploracion/p08_muestra.sql`

**Objetivo:** 3.5 muestra aleatoria de registros de cada tipo de taxi (las columnas exclusivas de un tipo quedan en NULL en el otro).

**Fuente:** /workspace/data/raw/yellow/*/*.parquet y /workspace/data/raw/green/*/*.parquet

**Consulta SQL:**

```sql
-- Objetivo: 3.5 muestra aleatoria de registros de cada tipo de taxi (las columnas exclusivas de un tipo quedan en NULL en el otro).
-- Fuente: /workspace/data/raw/yellow/*/*.parquet y /workspace/data/raw/green/*/*.parquet
-- Decision: la muestra confirma el esquema normalizado: zonas dentro de 1-265 y payment_type de 0 a 5 en yellow (1 a 5 y nulos en green). sin hallazgos adicionales.
SELECT 'yellow' AS tipo, * FROM (SELECT * FROM read_parquet('/workspace/data/raw/yellow/*/*.parquet', union_by_name = true) USING SAMPLE 5 ROWS)
UNION ALL BY NAME
SELECT 'green' AS tipo, * FROM (SELECT * FROM read_parquet('/workspace/data/raw/green/*/*.parquet', union_by_name = true) USING SAMPLE 5 ROWS);
```

**Resultado** (10 filas; se muestran 10; 0.56 s):

| tipo | VendorID | tpep_pickup_datetime | tpep_dropoff_datetime | passenger_count | trip_distance | RatecodeID | store_and_fwd_flag | PULocationID | DOLocationID | payment_type | fare_amount | extra | mta_tax | tip_amount | tolls_amount | improvement_surcharge | total_amount | congestion_surcharge | Airport_fee | cbd_congestion_fee | request_source | lpep_pickup_datetime | lpep_dropoff_datetime | ehail_fee | trip_type |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| yellow | 2 | 2024-01-01 00:33:58 | 2024-01-01 00:46:45 | 1 | 2.45 | 1 | N | 142 | 262 | 1 | 14.90 | 1.00 | 0.50 | 3.98 | 0.00 | 1.00 | 23.88 | 2.50 | 0.00 |  |  |  |  |  |  |
| yellow | 2 | 2024-01-01 01:39:29 | 2024-01-01 01:58:22 | 1 | 1.07 | 1 | N | 68 | 68 | 1 | 17.00 | 1.00 | 0.50 | 4.40 | 0.00 | 1.00 | 26.40 | 2.50 | 0.00 |  |  |  |  |  |  |
| yellow | 2 | 2024-01-01 02:55:35 | 2024-01-01 03:18:34 | 1 | 4.82 | 1 | N | 231 | 112 | 1 | 26.80 | 1.00 | 0.50 | 20.02 | 0.00 | 1.00 | 51.82 | 2.50 | 0.00 |  |  |  |  |  |  |
| yellow | 2 | 2024-01-01 03:13:33 | 2024-01-01 03:21:16 | 1 | 1.25 | 1 | N | 100 | 233 | 1 | 9.30 | 1.00 | 0.50 | 0.00 | 0.00 | 1.00 | 14.30 | 2.50 | 0.00 |  |  |  |  |  |  |
| yellow | 2 | 2024-01-01 03:10:37 | 2024-01-01 03:26:53 | 1 | 8.08 | 1 | N | 33 | 157 | 1 | 33.10 | 1.00 | 0.50 | 7.12 | 0.00 | 1.00 | 42.72 | 0.00 | 0.00 |  |  |  |  |  |  |
| green | 2 |  |  | 2 | 2.71 | 1 | N | 74 | 262 | 1 | 17.00 | 0.00 | 0.50 | 2.00 | 0.00 | 1.00 | 23.25 | 2.75 |  |  |  | 2024-03-02 16:59:46 | 2024-03-02 17:15:59 |  | 1 |
| green | 2 |  |  | 1 | 0.00 | 1 | N | 166 | 239 | 1 | 11.40 | 2.50 | 0.50 | 5.44 | 0.00 | 1.00 | 23.59 | 2.75 |  |  |  | 2024-04-01 16:17:48 | 2024-04-01 16:30:17 |  | 1 |
| green | 2 |  |  | 1 | 1.62 | 1 | N | 74 | 75 | 1 | 12.80 | 0.00 | 0.50 | 2.86 | 0.00 | 1.00 | 17.16 | 0.00 |  |  |  | 2024-04-02 13:26:39 | 2024-04-02 13:39:04 |  | 1 |
| green | 2 |  |  | 1 | 2.41 | 1 | N | 95 | 121 | 1 | 15.60 | 0.00 | 0.50 | 3.42 | 0.00 | 1.00 | 20.52 | 0.00 |  |  |  | 2024-04-03 13:04:46 | 2024-04-03 13:18:25 |  | 1 |
| green | 2 |  |  | 5 | 0.74 | 1 | N | 75 | 75 | 1 | 10.70 | 0.00 | 0.50 | 2.44 | 0.00 | 1.00 | 14.64 | 0.00 |  |  |  | 2024-04-04 14:13:31 | 2024-04-04 14:24:19 |  | 1 |

**Decision / interpretacion:** la muestra confirma el esquema normalizado: zonas dentro de 1-265 y payment_type de 0 a 5 en yellow (1 a 5 y nulos en green). sin hallazgos adicionales.

### `sql/01_exploracion/p09_resumen_yellow.sql`

**Objetivo:** 3.6 perfil estadistico de cada columna de yellow (minimo, maximo, cuartiles, % de nulos): permite ver valores imposibles.

**Fuente:** /workspace/data/raw/yellow/*/*.parquet

**Consulta SQL:**

```sql
-- Objetivo: 3.6 perfil estadistico de cada columna de yellow (minimo, maximo, cuartiles, % de nulos): permite ver valores imposibles.
-- Fuente: /workspace/data/raw/yellow/*/*.parquet
-- Decision: yellow: trip_distance llega a 398,608 millas y fare_amount a 863,372 (y minimo -2,555): hay valores imposibles. passenger_count, RatecodeID y store_and_fwd_flag tienen 19.6 % de nulos. las fechas van de 2001 a 2026.
SUMMARIZE SELECT * FROM read_parquet('/workspace/data/raw/yellow/*/*.parquet', union_by_name = true);
```

**Resultado** (21 filas; se muestran 15; 37.64 s):

| column_name | column_type | min | max | approx_unique | avg | std | q25 | q50 | q75 | count | null_percentage |
|---|---|---|---|---|---|---|---|---|---|---|---|
| VendorID | INTEGER | 1 | 7 | 4 | 1.8335070004244385 | 0.6161473518861239 | 2 | 2 | 2 | 119,595,677 | 0.00 |
| tpep_pickup_datetime | TIMESTAMP | 2001-01-01 09:23:58 | 2026-08-31 23:59:59 | 59,913,128 | 2025-05-15 18:14:36.687007 |  | 2024-09-29 16:17:53.273584 | 2025-05-23 18:25:03.904818 | 2025-12-30 20:43:31.991886 | 119,595,677 | 0.00 |
| tpep_dropoff_datetime | TIMESTAMP | 2001-01-01 16:09:38 | 2026-09-01 20:16:00 | 57,216,129 | 2025-05-15 18:32:04.653367 |  | 2024-10-01 01:50:48.466262 | 2025-05-23 04:37:38.268424 | 2025-12-29 01:16:42.514246 | 119,595,677 | 0.00 |
| passenger_count | BIGINT | 0 | 9 | 11 | 1.2997810895650606 | 0.7484946933744839 | 1 | 1 | 1 | 119,595,677 | 19.58 |
| trip_distance | DOUBLE | 0.0 | 398608.62 | 10,523 | 5.879887555051061 | 554.6138004037981 | 1.0275214946151237 | 1.8147596211753256 | 3.5970113567270245 | 119,595,677 | 0.00 |
| RatecodeID | BIGINT | 1 | 99 | 7 | 3.174698541566505 | 14.118714317547497 | 1 | 1 | 1 | 119,595,677 | 19.58 |
| store_and_fwd_flag | VARCHAR | N | Y | 2 |  |  |  |  |  | 119,595,677 | 19.58 |
| PULocationID | INTEGER | 1 | 265 | 298 | 162.46523230935847 | 65.71491450004342 | 123 | 161 | 233 | 119,595,677 | 0.00 |
| DOLocationID | INTEGER | 1 | 265 | 298 | 161.89985110414986 | 70.23822645090662 | 111 | 162 | 234 | 119,595,677 | 0.00 |
| payment_type | BIGINT | 0 | 5 | 6 | 0.9771172916225057 | 0.6976295922850972 | 1 | 1 | 1 | 119,595,677 | 0.00 |
| fare_amount | DOUBLE | -2555.2 | 863372.12 | 26,624 | 19.417722070563023 | 102.12534044444952 | 9.289796028370201 | 14.23751167513807 | 23.59931539228913 | 119,595,677 | 0.00 |
| extra | DOUBLE | -17.39 | 244.35 | 496 | 1.2278120382227502 | 1.8062026091351828 | 0.0 | 0.0 | 2.5 | 119,595,677 | 0.00 |
| mta_tax | DOUBLE | -21.74 | 5243.38 | 113 | 0.48102933988157487 | 0.49551668738794474 | 0.5 | 0.5 | 0.5 | 119,595,677 | 0.00 |
| tip_amount | DOUBLE | -333.33 | 999.99 | 8,438 | 2.999775045214615 | 4.01596133636095 | 0.0 | 2.3002228279988164 | 4.03963441140869 | 119,595,677 | 0.00 |
| tolls_amount | DOUBLE | -148.17 | 1702.88 | 5,456 | 0.5296646904693274 | 2.1893675955756993 | 0.0 | 0.0 | 0.0 | 119,595,677 | 0.00 |

**Decision / interpretacion:** yellow: trip_distance llega a 398,608 millas y fare_amount a 863,372 (y minimo -2,555): hay valores imposibles. passenger_count, RatecodeID y store_and_fwd_flag tienen 19.6 % de nulos. las fechas van de 2001 a 2026.

### `sql/01_exploracion/p10_resumen_green.sql`

**Objetivo:** 3.6 perfil estadistico de cada columna de green (minimo, maximo, cuartiles, % de nulos): permite ver valores imposibles.

**Fuente:** /workspace/data/raw/green/*/*.parquet

**Consulta SQL:**

```sql
-- Objetivo: 3.6 perfil estadistico de cada columna de green (minimo, maximo, cuartiles, % de nulos): permite ver valores imposibles.
-- Fuente: /workspace/data/raw/green/*/*.parquet
-- Decision: green tambien tiene distancias y tarifas extremas. ehail_fee es 100 % nulo, no se usa en ningun indicador.
SUMMARIZE SELECT * FROM read_parquet('/workspace/data/raw/green/*/*.parquet', union_by_name = true);
```

**Resultado** (22 filas; se muestran 15; 0.81 s):

| column_name | column_type | min | max | approx_unique | avg | std | q25 | q50 | q75 | count | null_percentage |
|---|---|---|---|---|---|---|---|---|---|---|---|
| VendorID | INTEGER | 1 | 6 | 3 | 2.0460078541858255 | 0.855294552279898 | 2 | 2 | 2 | 1,588,707 | 0.00 |
| lpep_pickup_datetime | TIMESTAMP | 2008-12-31 00:00:00 | 2026-08-31 23:58:28 | 1,571,774 | 2025-04-04 05:19:26.264852 |  | 2024-08-05 01:40:31.63433 | 2025-04-04 12:44:29.266007 | 2025-11-19 16:21:51.404988 | 1,588,707 | 0.00 |
| lpep_dropoff_datetime | TIMESTAMP | 2008-12-31 00:00:00 | 2026-09-02 09:39:37 | 1,740,542 | 2025-04-04 05:39:49.432621 |  | 2024-08-07 13:45:14.238764 | 2025-04-03 18:21:01.720154 | 2025-11-21 17:17:21.63074 | 1,588,707 | 0.00 |
| store_and_fwd_flag | VARCHAR | N | Y | 2 |  |  |  |  |  | 1,588,707 | 7.74 |
| RatecodeID | BIGINT | 1 | 99 | 7 | 1.2536759990284665 | 1.8724714003995142 | 1 | 1 | 1 | 1,588,707 | 7.74 |
| PULocationID | INTEGER | 1 | 265 | 266 | 96.73649640871476 | 56.76737114812791 | 74 | 75 | 104 | 1,588,707 | 0.00 |
| DOLocationID | INTEGER | 1 | 265 | 266 | 142.1635468339977 | 76.99613522856887 | 74 | 140 | 228 | 1,588,707 | 0.00 |
| passenger_count | BIGINT | 0 | 9 | 11 | 1.3039139701608216 | 0.9577964773685869 | 1 | 1 | 1 | 1,588,707 | 7.74 |
| trip_distance | DOUBLE | 0.0 | 262315.94 | 3,609 | 16.987296688439226 | 1050.528654393464 | 1.1890497635062942 | 1.9485410891178412 | 3.4500404952923005 | 1,588,707 | 0.00 |
| fare_amount | DOUBLE | -500.0 | 1676.7 | 7,254 | 17.971704329368627 | 17.667042718062866 | 9.301472915549285 | 13.691821056225438 | 20.469002326918222 | 1,588,707 | 0.00 |
| extra | DOUBLE | -7.5 | 12.5 | 32 | 0.8900914643165795 | 1.3875834923747694 | 0.0 | 0.0 | 1.0007205169762305 | 1,588,707 | 0.00 |
| mta_tax | DOUBLE | -0.5 | 61.5 | 10 | 0.5693664722318212 | 0.34812948675085537 | 0.5 | 0.5 | 0.5 | 1,588,707 | 0.00 |
| tip_amount | DOUBLE | -100.0 | 495.0 | 2,526 | 2.616680684355217 | 3.997549097159671 | 0.0 | 2.0349273778020263 | 3.8726809510110565 | 1,588,707 | 0.00 |
| tolls_amount | DOUBLE | -24.5 | 108.0 | 208 | 0.2575251509560794 | 1.4246022717682914 | 0.0 | 0.0 | 0.0 | 1,588,707 | 0.00 |
| ehail_fee | DOUBLE |  |  | 0 |  |  |  |  |  | 1,588,707 | 100.00 |

**Decision / interpretacion:** green tambien tiene distancias y tarifas extremas. ehail_fee es 100 % nulo, no se usa en ningun indicador.

### `sql/01_exploracion/p11_calidad_conteos.sql`

**Objetivo:** 3.6 cuantificar registros problematicos por tipo de taxi (fechas, duraciones, distancias, tarifas, pasajeros, zonas).

**Fuente:** /workspace/data/raw/yellow/*/*.parquet y /workspace/data/raw/green/*/*.parquet

**Consulta SQL:**

```sql
-- Objetivo: 3.6 cuantificar registros problematicos por tipo de taxi (fechas, duraciones, distancias, tarifas, pasajeros, zonas).
-- Fuente: /workspace/data/raw/yellow/*/*.parquet y /workspace/data/raw/green/*/*.parquet
-- Decision: yellow: 3.8 M tarifas <= 0, 3.1 M distancias <= 0, 1.7 M totales negativos, 24 M pasajeros nulo/0 (20 %). se filtra en cada consulta (distancia 0.1-100, tarifa 1-500, duracion 1-180 min); trips queda sin corregir.
WITH v AS (
    SELECT 'yellow' AS tipo, tpep_pickup_datetime AS recogida, tpep_dropoff_datetime AS bajada, passenger_count,
           trip_distance, fare_amount, total_amount, PULocationID, filename
    FROM read_parquet('/workspace/data/raw/yellow/*/*.parquet', union_by_name = true, filename = true)
    UNION ALL
    SELECT 'green', lpep_pickup_datetime, lpep_dropoff_datetime, passenger_count,
           trip_distance, fare_amount, total_amount, PULocationID, filename
    FROM read_parquet('/workspace/data/raw/green/*/*.parquet', union_by_name = true, filename = true))
SELECT tipo, count(*) AS registros,
       count_if(year(recogida) <> CAST(regexp_extract(filename, '(\d{4})-\d{2}\.parquet', 1) AS INTEGER)) AS recogida_fuera_del_anio_del_archivo,
       count_if(bajada < recogida)                                    AS bajada_antes_de_recogida,
       count_if(bajada - recogida > INTERVAL 24 HOUR)                 AS duracion_mayor_24h,
       count_if(trip_distance <= 0)                                   AS distancia_cero_o_negativa,
       count_if(trip_distance > 100)                                  AS distancia_mayor_100_millas,
       count_if(fare_amount <= 0)                                     AS tarifa_cero_o_negativa,
       count_if(total_amount < 0)                                     AS total_negativo,
       count_if(passenger_count IS NULL OR passenger_count = 0)       AS pasajeros_nulo_o_cero,
       count_if(PULocationID IS NULL OR PULocationID NOT BETWEEN 1 AND 265) AS zona_recogida_invalida
FROM v
GROUP BY tipo
ORDER BY tipo;
```

**Resultado** (2 filas; se muestran 2; 5.77 s):

| tipo | registros | recogida_fuera_del_anio_del_archivo | bajada_antes_de_recogida | duracion_mayor_24h | distancia_cero_o_negativa | distancia_mayor_100_millas | tarifa_cero_o_negativa | total_negativo | pasajeros_nulo_o_cero | zona_recogida_invalida |
|---|---|---|---|---|---|---|---|---|---|---|
| green | 1,588,707 | 55 | 1,351 | 6 | 71,224 | 516 | 13,015 | 4,971 | 142,558 | 0 |
| yellow | 119,595,677 | 102 | 3,820 | 845 | 3,131,494 | 5,706 | 3,798,269 | 1,744,900 | 24,172,589 | 0 |

**Decision / interpretacion:** yellow: 3.8 M tarifas <= 0, 3.1 M distancias <= 0, 1.7 M totales negativos, 24 M pasajeros nulo/0 (20 %). se filtra en cada consulta (distancia 0.1-100, tarifa 1-500, duracion 1-180 min); trips queda sin corregir.

### `sql/01_exploracion/p12_fechas_fuera_de_rango.sql`

**Objetivo:** 3.6 distribucion de los anios de recogida por tipo: revela fechas imposibles (p. ej. 2002 o 2009) dentro de archivos de 2024-2026.

**Fuente:** /workspace/data/raw/yellow/*/*.parquet y /workspace/data/raw/green/*/*.parquet

**Consulta SQL:**

```sql
-- Objetivo: 3.6 distribucion de los anios de recogida por tipo: revela fechas imposibles (p. ej. 2002 o 2009) dentro de archivos de 2024-2026.
-- Fuente: /workspace/data/raw/yellow/*/*.parquet y /workspace/data/raw/green/*/*.parquet
-- Decision: hay recogidas de 2001, 2002, 2007, 2008, 2009 y 2023 (pocas decenas de viajes por tipo). se excluyen del analisis temporal con el filtro 2024-2026.
SELECT 'yellow' AS tipo, year(tpep_pickup_datetime) AS anio_recogida, count(*) AS registros
FROM read_parquet('/workspace/data/raw/yellow/*/*.parquet', union_by_name = true) GROUP BY ALL
UNION ALL
SELECT 'green', year(lpep_pickup_datetime), count(*)
FROM read_parquet('/workspace/data/raw/green/*/*.parquet', union_by_name = true) GROUP BY ALL
ORDER BY tipo, anio_recogida;
```

**Resultado** (15 filas; se muestran 15; 1.38 s):

| tipo | anio_recogida | registros |
|---|---|---|
| green | 2008 | 10 |
| green | 2009 | 8 |
| green | 2023 | 2 |
| green | 2024 | 660,204 |
| green | 2025 | 591,369 |
| green | 2026 | 337,114 |
| yellow | 2001 | 1 |
| yellow | 2002 | 11 |
| yellow | 2007 | 1 |
| yellow | 2008 | 15 |
| yellow | 2009 | 30 |
| yellow | 2023 | 10 |
| yellow | 2024 | 41,169,685 |
| yellow | 2025 | 48,722,584 |
| yellow | 2026 | 29,703,340 |

**Decision / interpretacion:** hay recogidas de 2001, 2002, 2007, 2008, 2009 y 2023 (pocas decenas de viajes por tipo). se excluyen del analisis temporal con el filtro 2024-2026.

## Analisis exploratorio (Ej. 4)

### `sql/02_eda/d01_estadisticos_numericos.sql`

**Objetivo:** estadisticos descriptivos de las variables numericas clave por tipo de taxi.

**Fuente:** vista `trips` = Parquet de data/raw/{yellow,green}/*/*.parquet normalizados (scripts/taxi_common.py), o la tabla `trips` de taxi.duckdb.

**Consulta SQL:**

```sql
-- Objetivo: estadisticos descriptivos de las variables numericas clave por tipo de taxi.
-- Fuente: vista `trips` = Parquet de data/raw/{yellow,green}/*/*.parquet normalizados (scripts/taxi_common.py), o la tabla `trips` de taxi.duckdb.
-- Decision: la media engaña: distancia media yellow 5.88 vs mediana 1.81; green 16.99 vs 1.95, por distancias absurdas (maximo 398,608). se reporta mediana y percentiles, no promedios crudos.
SELECT taxi_type,
       count(*) AS n,
       round(avg(trip_distance), 2) AS dist_prom, round(median(trip_distance), 2) AS dist_mediana,
       round(quantile_cont(trip_distance, 0.99), 2) AS dist_p99, max(trip_distance) AS dist_max,
       round(avg(fare_amount), 2) AS tarifa_prom, round(median(fare_amount), 2) AS tarifa_mediana,
       round(quantile_cont(fare_amount, 0.99), 2) AS tarifa_p99, max(fare_amount) AS tarifa_max,
       round(avg(total_amount), 2) AS total_prom, round(stddev(total_amount), 2) AS total_desv
FROM trips
GROUP BY taxi_type
ORDER BY taxi_type;
```

**Resultado** (2 filas; se muestran 2; 46.84 s):

| taxi_type | n | dist_prom | dist_mediana | dist_p99 | dist_max | tarifa_prom | tarifa_mediana | tarifa_p99 | tarifa_max | total_prom | total_desv |
|---|---|---|---|---|---|---|---|---|---|---|---|
| green | 1,588,707 | 16.99 | 1.95 | 17.25 | 262,315.94 | 17.97 | 13.50 | 80.00 | 1,676.70 | 24.88 | 19.95 |
| yellow | 119,595,677 | 5.88 | 1.81 | 19.72 | 398,608.62 | 19.42 | 14.20 | 80.00 | 863,372.12 | 28.01 | 103.03 |

**Decision / interpretacion:** la media engaña: distancia media yellow 5.88 vs mediana 1.81; green 16.99 vs 1.95, por distancias absurdas (maximo 398,608). se reporta mediana y percentiles, no promedios crudos.

### `sql/02_eda/d02_calidad_datos.sql`

**Objetivo:** cuantificar problemas de calidad (registros sospechosos) por tipo de taxi.

**Fuente:** vista `trips` = Parquet de data/raw/{yellow,green}/*/*.parquet normalizados (scripts/taxi_common.py), o la tabla `trips` de taxi.duckdb.

**Consulta SQL:**

```sql
-- Objetivo: cuantificar problemas de calidad (registros sospechosos) por tipo de taxi.
-- Fuente: vista `trips` = Parquet de data/raw/{yellow,green}/*/*.parquet normalizados (scripts/taxi_common.py), o la tabla `trips` de taxi.duckdb.
-- Decision: yellow tiene 845 viajes de mas de 24 h y 3,820 con bajada antes de la recogida; 68 fechas fuera de 2024-2026. todos se excluyen de duracion, velocidad y series temporales.
SELECT taxi_type, count(*) AS viajes,
       count_if(dropoff_datetime < pickup_datetime)                    AS bajada_antes_de_recogida,
       count_if(dropoff_datetime - pickup_datetime > INTERVAL 24 HOUR) AS duracion_mayor_24h,
       count_if(trip_distance <= 0)                                    AS distancia_cero_o_negativa,
       count_if(fare_amount <= 0)                                      AS tarifa_cero_o_negativa,
       count_if(total_amount < 0)                                      AS total_negativo,
       count_if(passenger_count IS NULL OR passenger_count = 0)        AS pasajeros_nulo_o_cero,
       count_if(pu_location_id IS NULL OR pu_location_id NOT BETWEEN 1 AND 265) AS zona_recogida_invalida,
       count_if(pickup_datetime < TIMESTAMP '2024-01-01'
                OR pickup_datetime >= TIMESTAMP '2027-01-01')          AS fecha_fuera_de_2024_2026
FROM trips
GROUP BY taxi_type
ORDER BY taxi_type;
```

**Resultado** (2 filas; se muestran 2; 5.52 s):

| taxi_type | viajes | bajada_antes_de_recogida | duracion_mayor_24h | distancia_cero_o_negativa | tarifa_cero_o_negativa | total_negativo | pasajeros_nulo_o_cero | zona_recogida_invalida | fecha_fuera_de_2024_2026 |
|---|---|---|---|---|---|---|---|---|---|
| green | 1,588,707 | 1,351 | 6 | 71,224 | 13,015 | 4,971 | 142,558 | 0 | 20 |
| yellow | 119,595,677 | 3,820 | 845 | 3,131,494 | 3,798,269 | 1,744,900 | 24,172,589 | 0 | 68 |

**Decision / interpretacion:** yellow tiene 845 viajes de mas de 24 h y 3,820 con bajada antes de la recogida; 68 fechas fuera de 2024-2026. todos se excluyen de duracion, velocidad y series temporales.

### `sql/02_eda/d03_distribucion_distancia.sql`

**Objetivo:** histograma de distancia de viaje (millas) para ver forma de la distribucion y cola larga.

**Fuente:** vista `trips` = Parquet de data/raw/{yellow,green}/*/*.parquet normalizados (scripts/taxi_common.py), o la tabla `trips` de taxi.duckdb.

**Consulta SQL:**

```sql
-- Objetivo: histograma de distancia de viaje (millas) para ver forma de la distribucion y cola larga.
-- Fuente: vista `trips` = Parquet de data/raw/{yellow,green}/*/*.parquet normalizados (scripts/taxi_common.py), o la tabla `trips` de taxi.duckdb.
-- Decision: la mayoria de viajes es corta: ~47 % de yellow y 51 % de green estan entre 1 y 3 millas; <= 0 millas son 2.6 % (yellow) y 4.5 % (green). se filtra distancia > 0.1.
WITH r AS (
    SELECT taxi_type,
           CASE WHEN trip_distance <= 0 THEN '0. <= 0'
                WHEN trip_distance < 1 THEN '1. (0,1)'
                WHEN trip_distance < 3 THEN '2. [1,3)'
                WHEN trip_distance < 5 THEN '3. [3,5)'
                WHEN trip_distance < 10 THEN '4. [5,10)'
                WHEN trip_distance < 30 THEN '5. [10,30)'
                ELSE '6. >= 30' END AS rango_millas
    FROM trips
    WHERE trip_distance IS NOT NULL),
c AS (SELECT taxi_type, rango_millas, count(*) AS viajes FROM r GROUP BY ALL)
SELECT taxi_type, rango_millas, viajes,
       round(100.0 * viajes / sum(viajes) OVER (PARTITION BY taxi_type), 2) AS porcentaje
FROM c
ORDER BY taxi_type, rango_millas;
```

**Resultado** (14 filas; se muestran 14; 1.36 s):

| taxi_type | rango_millas | viajes | porcentaje |
|---|---|---|---|
| green | 0. <= 0 | 71,224 | 4.48 |
| green | 1. (0,1) | 228,237 | 14.37 |
| green | 2. [1,3) | 813,612 | 51.21 |
| green | 3. [3,5) | 232,908 | 14.66 |
| green | 4. [5,10) | 172,495 | 10.86 |
| green | 5. [10,30) | 68,591 | 4.32 |
| green | 6. >= 30 | 1,640 | 0.10 |
| yellow | 0. <= 0 | 3,131,494 | 2.62 |
| yellow | 1. (0,1) | 24,803,834 | 20.74 |
| yellow | 2. [1,3) | 55,342,883 | 46.27 |
| yellow | 3. [3,5) | 14,690,138 | 12.28 |
| yellow | 4. [5,10) | 12,332,295 | 10.31 |
| yellow | 5. [10,30) | 9,172,545 | 7.67 |
| yellow | 6. >= 30 | 122,488 | 0.10 |

**Decision / interpretacion:** la mayoria de viajes es corta: ~47 % de yellow y 51 % de green estan entre 1 y 3 millas; <= 0 millas son 2.6 % (yellow) y 4.5 % (green). se filtra distancia > 0.1.

### `sql/02_eda/d04_duracion_y_velocidad.sql`

**Objetivo:** duracion y velocidad promedio, usando solo viajes plausibles (1 min a 3 h, distancia > 0).

**Fuente:** vista `trips` = Parquet de data/raw/{yellow,green}/*/*.parquet normalizados (scripts/taxi_common.py), o la tabla `trips` de taxi.duckdb.

**Consulta SQL:**

```sql
-- Objetivo: duracion y velocidad promedio, usando solo viajes plausibles (1 min a 3 h, distancia > 0).
-- Fuente: vista `trips` = Parquet de data/raw/{yellow,green}/*/*.parquet normalizados (scripts/taxi_common.py), o la tabla `trips` de taxi.duckdb.
-- Decision: duracion mediana 13.6 min (yellow) y 12.6 (green). la velocidad media de green (67.7 mph) es imposible: viene de distancias absurdas, asi que hay que usar mediana o filtrar distancia <= 100.
WITH v AS (
    SELECT taxi_type, trip_distance,
           date_diff('second', pickup_datetime, dropoff_datetime) / 60.0 AS minutos
    FROM trips
    WHERE dropoff_datetime > pickup_datetime AND trip_distance > 0
)
SELECT taxi_type, count(*) AS viajes,
       round(avg(minutos), 1) AS duracion_prom_min,
       round(median(minutos), 1) AS duracion_mediana_min,
       round(quantile_cont(minutos, 0.95), 1) AS duracion_p95_min,
       round(sum(trip_distance) / (sum(minutos) / 60.0), 1) AS velocidad_prom_mph
FROM v
WHERE minutos BETWEEN 1 AND 180
GROUP BY taxi_type
ORDER BY taxi_type;
```

**Resultado** (2 filas; se muestran 2; 10.20 s):

| taxi_type | viajes | duracion_prom_min | duracion_mediana_min | duracion_p95_min | velocidad_prom_mph |
|---|---|---|---|---|---|
| green | 1,490,116 | 15.80 | 12.60 | 38.20 | 67.70 |
| yellow | 115,087,147 | 17.30 | 13.60 | 44.00 | 21.10 |

**Decision / interpretacion:** duracion mediana 13.6 min (yellow) y 12.6 (green). la velocidad media de green (67.7 mph) es imposible: viene de distancias absurdas, asi que hay que usar mediana o filtrar distancia <= 100.

### `sql/02_eda/d05_patron_hora_dia.sql`

**Objetivo:** demanda por dia de la semana (0 = domingo) y hora; sirve para un mapa de calor.

**Fuente:** vista `trips` = Parquet de data/raw/{yellow,green}/*/*.parquet normalizados (scripts/taxi_common.py), o la tabla `trips` de taxi.duckdb.

**Consulta SQL:**

```sql
-- Objetivo: demanda por dia de la semana (0 = domingo) y hora; sirve para un mapa de calor.
-- Fuente: vista `trips` = Parquet de data/raw/{yellow,green}/*/*.parquet normalizados (scripts/taxi_common.py), o la tabla `trips` de taxi.duckdb.
-- Decision: yellow: pico a las 18 h (8.5 M viajes), valle de 4 a 5 h; el lunes tiene menos viajes (14.6 M) y el jueves mas (18.6 M). el filtro fijo 2024-2026 es el unico limite de la consulta.
SELECT taxi_type,
       dayofweek(pickup_datetime) AS dia_semana,
       hour(pickup_datetime) AS hora,
       count(*) AS viajes,
       round(avg(total_amount), 2) AS total_prom
FROM trips
WHERE pickup_datetime >= TIMESTAMP '2024-01-01' AND pickup_datetime < TIMESTAMP '2027-01-01'
GROUP BY ALL
ORDER BY taxi_type, dia_semana, hora;
```

**Resultado** (336 filas; se muestran 15; 0.51 s):

| taxi_type | dia_semana | hora | viajes | total_prom |
|---|---|---|---|---|
| green | 0 | 0 | 6,144 | 27.78 |
| green | 0 | 1 | 4,979 | 29.42 |
| green | 0 | 2 | 4,162 | 34.42 |
| green | 0 | 3 | 3,656 | 38.54 |
| green | 0 | 4 | 2,972 | 41.58 |
| green | 0 | 5 | 1,803 | 40.65 |
| green | 0 | 6 | 2,020 | 33.19 |
| green | 0 | 7 | 3,302 | 33.31 |
| green | 0 | 8 | 4,436 | 30.14 |
| green | 0 | 9 | 6,630 | 27.09 |
| green | 0 | 10 | 7,728 | 24.09 |
| green | 0 | 11 | 9,096 | 23.65 |
| green | 0 | 12 | 10,992 | 23.17 |
| green | 0 | 13 | 11,170 | 23.49 |
| green | 0 | 14 | 12,539 | 24.02 |

**Decision / interpretacion:** yellow: pico a las 18 h (8.5 M viajes), valle de 4 a 5 h; el lunes tiene menos viajes (14.6 M) y el jueves mas (18.6 M). el filtro fijo 2024-2026 es el unico limite de la consulta.

### `sql/02_eda/d06_pago_y_propinas.sql`

**Objetivo:** metodo de pago y propinas. La propina solo se registra de forma confiable con tarjeta (payment_type = 1).

**Fuente:** vista `trips` = Parquet de data/raw/{yellow,green}/*/*.parquet normalizados (scripts/taxi_common.py), o la tabla `trips` de taxi.duckdb.

**Consulta SQL:**

```sql
-- Objetivo: metodo de pago y propinas. La propina solo se registra de forma confiable con tarjeta (payment_type = 1).
-- Fuente: vista `trips` = Parquet de data/raw/{yellow,green}/*/*.parquet normalizados (scripts/taxi_common.py), o la tabla `trips` de taxi.duckdb.
-- Decision: tarjeta es ~67 % de los viajes con propina media 4.33 (yellow) y efectivo 0.00: la propina en efectivo no se registra. en yellow, payment_type 0 (19.6 %) coincide con los nulos de passenger_count; analizar propinas solo con tarjeta.
WITH p AS (
    SELECT taxi_type, payment_type, count(*) AS viajes,
           round(avg(tip_amount), 2) AS propina_prom,
           round(avg(100.0 * tip_amount / fare_amount) FILTER (WHERE fare_amount > 0), 2) AS propina_pct_tarifa
    FROM trips
    GROUP BY ALL)
SELECT taxi_type, payment_type, viajes,
       round(100.0 * viajes / sum(viajes) OVER (PARTITION BY taxi_type), 2) AS pct_viajes,
       propina_prom, propina_pct_tarifa
FROM p
ORDER BY taxi_type, payment_type;
```

**Resultado** (12 filas; se muestran 12; 1.79 s):

| taxi_type | payment_type | viajes | pct_viajes | propina_prom | propina_pct_tarifa |
|---|---|---|---|---|---|
| green | 1 | 1,081,279 | 68.06 | 3.66 | 23.20 |
| green | 2 | 370,766 | 23.34 | 0.00 | 0.00 |
| green | 3 | 10,072 | 0.63 | 0.00 | 1.05 |
| green | 4 | 3,555 | 0.22 | 0.01 | 0.05 |
| green | 5 | 52 | 0.00 | 0.00 | 0.00 |
| green |  | 122,983 | 7.74 | 1.63 | 6.99 |
| yellow | 0 | 23,419,814 | 19.58 | 0.43 | 2.09 |
| yellow | 1 | 80,447,167 | 67.27 | 4.33 | 26.14 |
| yellow | 2 | 12,902,464 | 10.79 | 0.00 | 0.00 |
| yellow | 3 | 698,028 | 0.58 | 0.01 | 0.10 |
| yellow | 4 | 2,128,195 | 1.78 | 0.03 | 0.06 |
| yellow | 5 | 9 | 0.00 | 0.00 | 0.00 |

**Decision / interpretacion:** tarjeta es ~67 % de los viajes con propina media 4.33 (yellow) y efectivo 0.00: la propina en efectivo no se registra. en yellow, payment_type 0 (19.6 %) coincide con los nulos de passenger_count; analizar propinas solo con tarjeta.

### `sql/02_eda/d07_zonas_recogida_destino.sql`

**Objetivo:** zonas mas activas como origen y como destino (IDs de zona de la TLC; sin tabla de nombres en el repo).

**Fuente:** vista `trips` = Parquet de data/raw/{yellow,green}/*/*.parquet normalizados (scripts/taxi_common.py), o la tabla `trips` de taxi.duckdb.

**Consulta SQL:**

```sql
-- Objetivo: zonas mas activas como origen y como destino (IDs de zona de la TLC; sin tabla de nombres en el repo).
-- Fuente: vista `trips` = Parquet de data/raw/{yellow,green}/*/*.parquet normalizados (scripts/taxi_common.py), o la tabla `trips` de taxi.duckdb.
-- Decision: las zonas 237, 132 y 161 concentran mas recogidas (132 es JFK: 5.2 M recogidas vs 1.2 M bajadas, saldo neto +4 M). las zonas son ids sin nombre; falta la tabla de zonas para presentar nombres.
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
```

**Resultado** (25 filas; se muestran 15; 1.16 s):

| zona | recogidas | bajadas | saldo_neto |
|---|---|---|---|
| 237 | 5,348,392 | 4,857,696 | 490,696 |
| 132 | 5,234,798 | 1,199,177 | 4,035,621 |
| 161 | 5,227,622 | 4,285,768 | 941,854 |
| 236 | 4,783,937 | 5,013,328 | -229,391 |
| 162 | 3,829,302 | 3,255,901 | 573,401 |
| 186 | 3,809,837 | 2,577,041 | 1,232,796 |
| 230 | 3,760,742 | 3,583,571 | 177,171 |
| 142 | 3,550,484 | 3,148,211 | 402,273 |
| 138 | 3,328,127 | 1,278,561 | 2,049,566 |
| 170 | 3,247,812 | 3,384,195 | -136,383 |
| 234 | 3,161,526 | 2,807,198 | 354,328 |
| 163 | 3,131,710 | 2,811,200 | 320,510 |
| 239 | 3,126,983 | 3,147,247 | -20,264 |
| 68 | 3,122,029 | 3,070,140 | 51,889 |
| 79 | 2,961,102 | 2,605,885 | 355,217 |

**Decision / interpretacion:** las zonas 237, 132 y 161 concentran mas recogidas (132 es JFK: 5.2 M recogidas vs 1.2 M bajadas, saldo neto +4 M). las zonas son ids sin nombre; falta la tabla de zonas para presentar nombres.

### `sql/02_eda/d08_correlaciones.sql`

**Objetivo:** correlacion entre variables numericas (viajes con valores positivos y plausibles).

**Fuente:** vista `trips` = Parquet de data/raw/{yellow,green}/*/*.parquet normalizados (scripts/taxi_common.py), o la tabla `trips` de taxi.duckdb.

**Consulta SQL:**

```sql
-- Objetivo: correlacion entre variables numericas (viajes con valores positivos y plausibles).
-- Fuente: vista `trips` = Parquet de data/raw/{yellow,green}/*/*.parquet normalizados (scripts/taxi_common.py), o la tabla `trips` de taxi.duckdb.
-- Decision: distancia y tarifa se correlacionan fuerte en yellow (0.91) y menos en green (0.74); pasajeros casi no influye (0.03-0.06). la distancia es el mejor predictor de ingreso.
SELECT taxi_type,
       round(corr(trip_distance, fare_amount), 3) AS corr_distancia_tarifa,
       round(corr(trip_distance, total_amount), 3) AS corr_distancia_total,
       round(corr(fare_amount, tip_amount), 3)     AS corr_tarifa_propina,
       round(corr(passenger_count, total_amount), 3) AS corr_pasajeros_total
FROM trips
WHERE trip_distance BETWEEN 0.1 AND 100 AND fare_amount BETWEEN 1 AND 500
GROUP BY taxi_type
ORDER BY taxi_type;
```

**Resultado** (2 filas; se muestran 2; 0.83 s):

| taxi_type | corr_distancia_tarifa | corr_distancia_total | corr_tarifa_propina | corr_pasajeros_total |
|---|---|---|---|---|
| green | 0.74 | 0.84 | 0.42 | 0.03 |
| yellow | 0.91 | 0.90 | 0.53 | 0.06 |

**Decision / interpretacion:** distancia y tarifa se correlacionan fuerte en yellow (0.91) y menos en green (0.74); pasajeros casi no influye (0.03-0.06). la distancia es el mejor predictor de ingreso.

### `sql/02_eda/d09_atipicos_iqr.sql`

**Objetivo:** valores atipicos de tarifa con el criterio del rango intercuartil (IQR), por tipo de taxi.

**Fuente:** vista `trips` = Parquet de data/raw/{yellow,green}/*/*.parquet normalizados (scripts/taxi_common.py), o la tabla `trips` de taxi.duckdb.

**Consulta SQL:**

```sql
-- Objetivo: valores atipicos de tarifa con el criterio del rango intercuartil (IQR), por tipo de taxi.
-- Fuente: vista `trips` = Parquet de data/raw/{yellow,green}/*/*.parquet normalizados (scripts/taxi_common.py), o la tabla `trips` de taxi.duckdb.
-- Decision: por IQR ~8 % de las tarifas son atipicas altas (yellow limite 45.63, 9.45 M viajes). es demasiado porcentaje para eliminarlos: son viajes largos legitimos, asi que se usa el filtro fijo 1-500 y no el IQR.
WITH lim AS (
    SELECT taxi_type,
           quantile_cont(fare_amount, 0.25) AS q1,
           quantile_cont(fare_amount, 0.75) AS q3
    FROM trips WHERE fare_amount > 0
    GROUP BY taxi_type)
SELECT t.taxi_type, round(l.q1, 2) AS q1, round(l.q3, 2) AS q3,
       round(l.q3 + 1.5 * (l.q3 - l.q1), 2) AS limite_superior,
       count(*) FILTER (WHERE t.fare_amount > l.q3 + 1.5 * (l.q3 - l.q1)) AS atipicos_altos,
       round(100.0 * count(*) FILTER (WHERE t.fare_amount > l.q3 + 1.5 * (l.q3 - l.q1)) / count(*), 2) AS pct_atipicos
FROM trips t JOIN lim l USING (taxi_type)
WHERE t.fare_amount > 0
GROUP BY t.taxi_type, l.q1, l.q3
ORDER BY t.taxi_type;
```

**Resultado** (2 filas; se muestran 2; 11.97 s):

| taxi_type | q1 | q3 | limite_superior | atipicos_altos | pct_atipicos |
|---|---|---|---|---|---|
| green | 9.30 | 20.50 | 37.30 | 123,447 | 7.83 |
| yellow | 9.58 | 24.00 | 45.63 | 9,450,800 | 8.16 |

**Decision / interpretacion:** por IQR ~8 % de las tarifas son atipicas altas (yellow limite 45.63, 9.45 M viajes). es demasiado porcentaje para eliminarlos: son viajes largos legitimos, asi que se usa el filtro fijo 1-500 y no el IQR.

### `sql/02_eda/d10_tendencia_mensual.sql`

**Objetivo:** comportamiento temporal. Viajes e ingresos por mes de recogida y tipo de taxi (tendencia y estacionalidad).

**Fuente:** vista `trips` = Parquet de data/raw/{yellow,green}/*/*.parquet normalizados (scripts/taxi_common.py), o la tabla `trips` de taxi.duckdb.

**Consulta SQL:**

```sql
-- Objetivo: comportamiento temporal. Viajes e ingresos por mes de recogida y tipo de taxi (tendencia y estacionalidad).
-- Fuente: vista `trips` = Parquet de data/raw/{yellow,green}/*/*.parquet normalizados (scripts/taxi_common.py), o la tabla `trips` de taxi.duckdb.
-- Decision: 64 filas (32 meses por tipo). yellow sube 13-27 % de 2024 a 2025 y baja 3.5-11.2 % de 2025 a 2026 (feb-ago; enero 2026 sube 7.2 %); green baja todos los meses. 2026 llega solo hasta agosto, por eso no se compara anio completo.
SELECT taxi_type, date_trunc('month', pickup_datetime) AS mes,
       count(*) AS viajes,
       round(sum(total_amount), 0) AS ingresos,
       round(avg(total_amount), 2) AS total_prom
FROM trips
WHERE pickup_datetime >= TIMESTAMP '2024-01-01' AND pickup_datetime < TIMESTAMP '2027-01-01'
  AND total_amount BETWEEN 0 AND 1000
GROUP BY ALL
ORDER BY taxi_type, mes;
```

**Resultado** (64 filas; se muestran 15; 0.94 s):

| taxi_type | mes | viajes | ingresos | total_prom |
|---|---|---|---|---|
| green | 2024-01-01 00:00:00 | 56,369 | 1.268e+06 | 22.49 |
| green | 2024-02-01 00:00:00 | 53,403 | 1.215e+06 | 22.75 |
| green | 2024-03-01 00:00:00 | 57,254 | 1.318e+06 | 23.02 |
| green | 2024-04-01 00:00:00 | 56,257 | 1.322e+06 | 23.51 |
| green | 2024-05-01 00:00:00 | 60,781 | 1.502e+06 | 24.71 |
| green | 2024-06-01 00:00:00 | 54,556 | 1.364e+06 | 24.99 |
| green | 2024-07-01 00:00:00 | 51,641 | 1.286e+06 | 24.90 |
| green | 2024-08-01 00:00:00 | 51,622 | 1.348e+06 | 26.12 |
| green | 2024-09-01 00:00:00 | 54,261 | 1.455e+06 | 26.81 |
| green | 2024-10-01 00:00:00 | 55,999 | 1.408e+06 | 25.14 |
| green | 2024-11-01 00:00:00 | 52,069 | 1.265e+06 | 24.29 |
| green | 2024-12-01 00:00:00 | 53,818 | 1.297e+06 | 24.10 |
| green | 2025-01-01 00:00:00 | 48,147 | 1.095e+06 | 22.75 |
| green | 2025-02-01 00:00:00 | 46,479 | 1.069e+06 | 23.00 |
| green | 2025-03-01 00:00:00 | 51,390 | 1.238e+06 | 24.09 |

**Decision / interpretacion:** 64 filas (32 meses por tipo). yellow sube 13-27 % de 2024 a 2025 y baja 3.5-11.2 % de 2025 a 2026 (feb-ago; enero 2026 sube 7.2 %); green baja todos los meses. 2026 llega solo hasta agosto, por eso no se compara anio completo.

### `sql/02_eda/d11_comparacion_yellow_green.sql`

**Objetivo:** diferencias entre taxis amarillos y verdes en una sola tabla (volumen, distancia, duracion, tarifa, propina, pasajeros, tarjeta). Solo viajes plausibles: distancia 0.1-100 millas, tarifa 1-500, duracion 1-180 minutos.

**Fuente:** vista `trips` = Parquet de data/raw/{yellow,green}/*/*.parquet normalizados (scripts/taxi_common.py), o la tabla `trips` de taxi.duckdb.

**Consulta SQL:**

```sql
-- Objetivo: diferencias entre taxis amarillos y verdes en una sola tabla (volumen, distancia, duracion, tarifa, propina, pasajeros, tarjeta).
-- Solo viajes plausibles: distancia 0.1-100 millas, tarifa 1-500, duracion 1-180 minutos.
-- Fuente: vista `trips` = Parquet de data/raw/{yellow,green}/*/*.parquet normalizados (scripts/taxi_common.py), o la tabla `trips` de taxi.duckdb.
-- Decision: yellow es mas caro (tarifa 20.23 vs 17.73) y largo (3.49 vs 3.13 mi); solo yellow sale de JFK/LGA (7.2 %). se pueden analizar juntos con la columna taxi_type, pero no promediar mezclados.
WITH v AS (
    SELECT *, date_diff('second', pickup_datetime, dropoff_datetime) / 60.0 AS minutos
    FROM trips
    WHERE trip_distance BETWEEN 0.1 AND 100 AND fare_amount BETWEEN 1 AND 500
      AND dropoff_datetime > pickup_datetime)
SELECT taxi_type,
       count(*) AS viajes,
       round(avg(trip_distance), 2) AS distancia_prom_millas,
       round(avg(minutos), 1) AS duracion_prom_min,
       round(avg(fare_amount), 2) AS tarifa_prom,
       round(avg(tip_amount), 2) AS propina_prom,
       round(avg(total_amount), 2) AS total_prom,
       round(avg(passenger_count), 2) AS pasajeros_prom,
       round(100.0 * count_if(payment_type = 1) / count(*), 1) AS pct_pago_tarjeta,
       round(100.0 * count_if(pu_location_id IN (132, 138)) / count(*), 1) AS pct_recogida_aeropuertos_jfk_lga
FROM v
WHERE minutos BETWEEN 1 AND 180
GROUP BY taxi_type
ORDER BY taxi_type;
```

**Resultado** (2 filas; se muestran 2; 1.39 s):

| taxi_type | viajes | distancia_prom_millas | duracion_prom_min | tarifa_prom | propina_prom | total_prom | pasajeros_prom | pct_pago_tarjeta | pct_recogida_aeropuertos_jfk_lga |
|---|---|---|---|---|---|---|---|---|---|
| green | 1,477,224 | 3.13 | 15.70 | 17.73 | 2.69 | 24.72 | 1.31 | 68.70 | 0.00 |
| yellow | 111,160,167 | 3.49 | 17.30 | 20.23 | 3.13 | 29.10 | 1.30 | 70.90 | 7.20 |

**Decision / interpretacion:** yellow es mas caro (tarifa 20.23 vs 17.73) y largo (3.49 vs 3.13 mi); solo yellow sale de JFK/LGA (7.2 %). se pueden analizar juntos con la columna taxi_type, pero no promediar mezclados.

## Validacion al incorporar anios (Ej. 5 y 8.3)

### `sql/03_validacion_anios/v00_consulta_conjunta_parquet.sql`

**Objetivo:** 5.6 comprobar, leyendo directamente los Parquet con un comodin, que se pueden consultar juntos 2024, 2025 y 2026 (archivos, registros y rango de fechas por anio y tipo). Sin tabla materializada.

**Fuente:** /workspace/data/raw/*/*/*.parquet

**Consulta SQL:**

```sql
-- Objetivo: 5.6 comprobar, leyendo directamente los Parquet con un comodin, que se pueden consultar juntos 2024, 2025 y 2026
-- (archivos, registros y rango de fechas por anio y tipo). Sin tabla materializada.
-- Fuente: /workspace/data/raw/*/*/*.parquet
-- Decision: una sola consulta con comodin lee 2024, 2025 y 2026 de ambos tipos (6 filas). los anios se pueden consultar juntos sin cambiar nada.
SELECT regexp_extract(filename, 'raw/([^/]+)/', 1) AS tipo,
       regexp_extract(filename, '/(\d{4})/', 1)    AS anio,
       count(DISTINCT filename) AS archivos,
       count(*) AS registros,
       min(coalesce(tpep_pickup_datetime, lpep_pickup_datetime)) AS primera_recogida,
       max(coalesce(tpep_pickup_datetime, lpep_pickup_datetime)) AS ultima_recogida
FROM read_parquet('/workspace/data/raw/*/*/*.parquet', union_by_name = true, filename = true)
GROUP BY ALL
ORDER BY tipo, anio;
```

**Resultado** (6 filas; se muestran 6; 2.11 s):

| tipo | anio | archivos | registros | primera_recogida | ultima_recogida |
|---|---|---|---|---|---|
| green | 2024 | 12 | 660,218 | 2008-12-31 00:00:00 | 2025-01-01 22:21:15 |
| green | 2025 | 12 | 591,375 | 2008-12-31 15:13:04 | 2026-01-01 21:09:39 |
| green | 2026 | 8 | 337,114 | 2008-12-31 17:35:31 | 2026-08-31 23:58:28 |
| yellow | 2024 | 12 | 41,169,720 | 2002-12-31 16:46:07 | 2026-06-26 23:53:12 |
| yellow | 2025 | 12 | 48,722,602 | 2007-12-05 18:45:00 | 2025-12-31 23:59:59 |
| yellow | 2026 | 8 | 29,703,355 | 2001-01-01 09:23:58 | 2026-08-31 23:59:59 |

**Decision / interpretacion:** una sola consulta con comodin lee 2024, 2025 y 2026 de ambos tipos (6 filas). los anios se pueden consultar juntos sin cambiar nada.

### `sql/03_validacion_anios/v01_viajes_por_anio_mes.sql`

**Objetivo:** confirmar que cada archivo mensual aporta filas (conteo por anio, mes y tipo segun el ARCHIVO de origen).

**Fuente:** vista `trips` = Parquet de data/raw/{yellow,green}/*/*.parquet normalizados (scripts/taxi_common.py), o la tabla `trips` de taxi.duckdb.

**Consulta SQL:**

```sql
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
```

**Resultado** (32 filas; se muestran 15; 0.23 s):

| anio | mes | yellow | green | total |
|---|---|---|---|---|
| 2024 | 1 | 2,964,624 | 56,551 | 3,021,175 |
| 2024 | 2 | 3,007,526 | 53,577 | 3,061,103 |
| 2024 | 3 | 3,582,628 | 57,457 | 3,640,085 |
| 2024 | 4 | 3,514,289 | 56,471 | 3,570,760 |
| 2024 | 5 | 3,723,833 | 61,003 | 3,784,836 |
| 2024 | 6 | 3,539,193 | 54,748 | 3,593,941 |
| 2024 | 7 | 3,076,903 | 51,837 | 3,128,740 |
| 2024 | 8 | 2,979,183 | 51,771 | 3,030,954 |
| 2024 | 9 | 3,633,030 | 54,440 | 3,687,470 |
| 2024 | 10 | 3,833,771 | 56,147 | 3,889,918 |
| 2024 | 11 | 3,646,369 | 52,222 | 3,698,591 |
| 2024 | 12 | 3,668,371 | 53,994 | 3,722,365 |
| 2025 | 1 | 3,475,226 | 48,326 | 3,523,552 |
| 2025 | 2 | 3,577,543 | 46,621 | 3,624,164 |
| 2025 | 3 | 4,145,257 | 51,539 | 4,196,796 |

**Decision / interpretacion:** 32 meses (12 + 12 + 8): en todos hay filas de yellow y de green, ningun mes queda en cero.

### `sql/03_validacion_anios/v02_meses_faltantes.sql`

**Objetivo:** detectar meses sin archivo entre el primero y el ultimo cargado, por tipo de taxi. Un mes final ausente puede ser normal (la TLC publica con atraso); un hueco intermedio no.

**Fuente:** vista `trips` = Parquet de data/raw/{yellow,green}/*/*.parquet normalizados (scripts/taxi_common.py), o la tabla `trips` de taxi.duckdb.

**Consulta SQL:**

```sql
-- Objetivo: detectar meses sin archivo entre el primero y el ultimo cargado, por tipo de taxi.
-- Un mes final ausente puede ser normal (la TLC publica con atraso); un hueco intermedio no.
-- Fuente: vista `trips` = Parquet de data/raw/{yellow,green}/*/*.parquet normalizados (scripts/taxi_common.py), o la tabla `trips` de taxi.duckdb.
-- Decision: 0 filas: no hay huecos entre el primer y el ultimo mes de cada tipo. sep-dic 2026 no es hueco: la tlc aun no lo publica.
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
```

**Resultado** (0 filas; se muestran 0; 0.19 s):

| taxi_type | mes_faltante |
|---|---|

**Decision / interpretacion:** 0 filas: no hay huecos entre el primer y el ultimo mes de cada tipo. sep-dic 2026 no es hueco: la tlc aun no lo publica.

### `sql/03_validacion_anios/v03_fechas_fuera_de_su_archivo.sql`

**Objetivo:** viajes cuya fecha de recogida no corresponde al mes del archivo (error de captura o de la fuente).

**Fuente:** vista `trips` = Parquet de data/raw/{yellow,green}/*/*.parquet normalizados (scripts/taxi_common.py), o la tabla `trips` de taxi.duckdb.

**Consulta SQL:**

```sql
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
```

**Resultado** (30 filas; se muestran 15; 0.14 s):

| anio_archivo | mes_archivo | taxi_type | viajes_fuera_de_mes | fecha_min | fecha_max |
|---|---|---|---|---|---|
| 2024 | 6 | yellow | 51 | 2008-12-31 00:00:00 | 2026-06-26 23:53:12 |
| 2024 | 8 | yellow | 51 | 2009-01-01 00:02:52 | 2024-09-10 12:27:29 |
| 2024 | 11 | yellow | 50 | 2002-12-31 22:17:43 | 2024-12-01 22:04:33 |
| 2024 | 9 | yellow | 49 | 2008-12-31 23:03:46 | 2024-10-01 21:24:53 |
| 2024 | 7 | yellow | 47 | 2009-01-01 00:02:24 | 2024-08-01 23:51:57 |
| 2026 | 7 | yellow | 46 | 2008-12-30 23:06:00 | 2026-08-05 20:54:00 |
| 2025 | 1 | green | 43 | 2024-12-25 23:13:15 | 2025-02-05 18:46:24 |
| 2024 | 10 | yellow | 40 | 2009-01-01 00:35:59 | 2024-11-14 18:30:00 |
| 2024 | 12 | yellow | 34 | 2008-12-31 23:03:59 | 2025-03-23 20:42:06 |
| 2024 | 9 | green | 34 | 2008-12-31 00:00:00 | 2024-10-01 23:42:50 |
| 2025 | 3 | yellow | 33 | 2007-12-05 18:45:00 | 2025-04-01 00:00:17 |
| 2025 | 9 | green | 33 | 2025-08-25 16:23:11 | 2025-10-01 20:08:10 |
| 2024 | 5 | yellow | 33 | 2002-12-31 16:46:07 | 2024-06-01 23:54:14 |
| 2025 | 2 | yellow | 31 | 2025-01-31 22:22:53 | 2025-03-01 00:06:32 |
| 2025 | 12 | green | 26 | 2008-12-31 15:13:04 | 2026-01-01 21:09:39 |

**Decision / interpretacion:** los 64 archivos tienen entre 2 y 51 viajes fuera de su mes (algunos de 2002-2009). son pocos; se excluyen con el filtro de fechas y no se borran de trips.

### `sql/03_validacion_anios/v04_columnas_por_anio.sql`

**Objetivo:** % de filas NO nulas de las columnas que cambian entre anios (esquema evolutivo). cbd_congestion_fee aparece desde 2025; airport_fee solo en yellow; ehail_fee/trip_type solo en green.

**Fuente:** vista `trips` = Parquet de data/raw/{yellow,green}/*/*.parquet normalizados (scripts/taxi_common.py), o la tabla `trips` de taxi.duckdb.

**Consulta SQL:**

```sql
-- Objetivo: % de filas NO nulas de las columnas que cambian entre anios (esquema evolutivo).
-- cbd_congestion_fee aparece desde 2025; airport_fee solo en yellow; ehail_fee/trip_type solo en green.
-- Fuente: vista `trips` = Parquet de data/raw/{yellow,green}/*/*.parquet normalizados (scripts/taxi_common.py), o la tabla `trips` de taxi.duckdb.
-- Decision: cbd_congestion_fee es 0 % en 2024 y ~100 % desde 2025; airport_fee baja de 90 % a 74 % en yellow. no sumar cargos entre anios sin considerar que la columna no existia.
SELECT source_year AS anio, taxi_type, count(*) AS filas,
       round(100.0 * count(cbd_congestion_fee) / count(*), 1) AS pct_cbd_congestion_fee,
       round(100.0 * count(airport_fee) / count(*), 1)        AS pct_airport_fee,
       round(100.0 * count(congestion_surcharge) / count(*), 1) AS pct_congestion_surcharge,
       round(100.0 * count(ehail_fee) / count(*), 1)          AS pct_ehail_fee,
       round(100.0 * count(trip_type) / count(*), 1)          AS pct_trip_type
FROM trips
GROUP BY ALL
ORDER BY anio, taxi_type;
```

**Resultado** (6 filas; se muestran 6; 1.26 s):

| anio | taxi_type | filas | pct_cbd_congestion_fee | pct_airport_fee | pct_congestion_surcharge | pct_ehail_fee | pct_trip_type |
|---|---|---|---|---|---|---|---|
| 2024 | green | 660,218 | 0.00 | 0.00 | 96.30 | 0.00 | 96.30 |
| 2024 | yellow | 41,169,720 | 0.00 | 90.10 | 90.10 | 0.00 | 0.00 |
| 2025 | green | 591,375 | 99.40 | 0.00 | 91.60 | 0.00 | 91.60 |
| 2025 | yellow | 48,722,602 | 100.00 | 76.20 | 76.20 | 0.00 | 0.00 |
| 2026 | green | 337,114 | 100.00 | 0.00 | 85.50 | 0.00 | 85.50 |
| 2026 | yellow | 29,703,355 | 100.00 | 74.00 | 74.00 | 0.00 | 0.00 |

**Decision / interpretacion:** cbd_congestion_fee es 0 % en 2024 y ~100 % desde 2025; airport_fee baja de 90 % a 74 % en yellow. no sumar cargos entre anios sin considerar que la columna no existia.

### `sql/03_validacion_anios/v05_metricas_por_anio.sql`

**Objetivo:** comparar metricas clave entre anios para detectar cambios bruscos o inconsistencias (solo viajes plausibles).

**Fuente:** vista `trips` = Parquet de data/raw/{yellow,green}/*/*.parquet normalizados (scripts/taxi_common.py), o la tabla `trips` de taxi.duckdb.

**Consulta SQL:**

```sql
-- Objetivo: comparar metricas clave entre anios para detectar cambios bruscos o inconsistencias (solo viajes plausibles).
-- Fuente: vista `trips` = Parquet de data/raw/{yellow,green}/*/*.parquet normalizados (scripts/taxi_common.py), o la tabla `trips` de taxi.duckdb.
-- Decision: metricas estables entre anios (distancia ~3.4-3.5, tarifa ~20 en yellow). 2026 tiene menos viajes por estar incompleto, no por una caida real.
SELECT source_year AS anio, taxi_type,
       count(*) AS viajes,
       round(avg(trip_distance), 2) AS dist_prom,
       round(avg(fare_amount), 2)   AS tarifa_prom,
       round(avg(tip_amount), 2)    AS propina_prom,
       round(avg(total_amount), 2)  AS total_prom,
       round(sum(total_amount) / 1e6, 2) AS ingresos_millones
FROM trips
WHERE trip_distance BETWEEN 0.1 AND 100 AND fare_amount BETWEEN 1 AND 500
GROUP BY ALL
ORDER BY anio, taxi_type;
```

**Resultado** (6 filas; se muestran 6; 0.64 s):

| anio | taxi_type | viajes | dist_prom | tarifa_prom | propina_prom | total_prom | ingresos_millones |
|---|---|---|---|---|---|---|---|
| 2024 | green | 618,682 | 2.97 | 18.13 | 2.66 | 24.21 | 14.98 |
| 2024 | yellow | 39,529,701 | 3.44 | 19.79 | 3.39 | 28.63 | 1,131.85 |
| 2025 | green | 558,644 | 3.21 | 17.94 | 2.73 | 25.17 | 14.06 |
| 2025 | yellow | 44,315,588 | 3.50 | 19.98 | 3.06 | 28.83 | 1,277.67 |
| 2026 | green | 316,704 | 3.34 | 17.09 | 2.65 | 25.46 | 8.06 |
| 2026 | yellow | 28,364,510 | 3.53 | 21.16 | 2.90 | 30.13 | 854.66 |

**Decision / interpretacion:** metricas estables entre anios (distancia ~3.4-3.5, tarifa ~20 en yellow). 2026 tiene menos viajes por estar incompleto, no por una caida real.

### `sql/03_validacion_anios/v06_comparacion_mismo_mes.sql`

**Objetivo:** variacion interanual de viajes comparando el mismo mes entre anios consecutivos.

**Fuente:** vista `trips` = Parquet de data/raw/{yellow,green}/*/*.parquet normalizados (scripts/taxi_common.py), o la tabla `trips` de taxi.duckdb.

**Consulta SQL:**

```sql
-- Objetivo: variacion interanual de viajes comparando el mismo mes entre anios consecutivos.
-- Fuente: vista `trips` = Parquet de data/raw/{yellow,green}/*/*.parquet normalizados (scripts/taxi_common.py), o la tabla `trips` de taxi.duckdb.
-- Decision: green baja todos los meses frente al mismo mes del anio anterior (de -7.0 % a -19.8 %); yellow sube 13-27 % en 2025 y baja 3.5-11.2 % en 2026 (feb-ago). se compara siempre el mismo mes, nunca anio completo contra 2026.
WITH m AS (
    SELECT taxi_type, source_year AS anio, source_month AS mes, count(*) AS viajes
    FROM trips GROUP BY ALL)
SELECT taxi_type, anio, mes, viajes,
       lag(viajes) OVER (PARTITION BY taxi_type, mes ORDER BY anio) AS viajes_anio_anterior,
       round(100.0 * (viajes - lag(viajes) OVER (PARTITION BY taxi_type, mes ORDER BY anio))
             / NULLIF(lag(viajes) OVER (PARTITION BY taxi_type, mes ORDER BY anio), 0), 1) AS variacion_pct
FROM m
ORDER BY taxi_type, mes, anio;
```

**Resultado** (64 filas; se muestran 15; 0.19 s):

| taxi_type | anio | mes | viajes | viajes_anio_anterior | variacion_pct |
|---|---|---|---|---|---|
| green | 2024 | 1 | 56,551 |  |  |
| green | 2025 | 1 | 48,326 | 56,551 | -14.50 |
| green | 2026 | 1 | 40,272 | 48,326 | -16.70 |
| green | 2024 | 2 | 53,577 |  |  |
| green | 2025 | 2 | 46,621 | 53,577 | -13.00 |
| green | 2026 | 2 | 37,373 | 46,621 | -19.80 |
| green | 2024 | 3 | 57,457 |  |  |
| green | 2025 | 3 | 51,539 | 57,457 | -10.30 |
| green | 2026 | 3 | 44,208 | 51,539 | -14.20 |
| green | 2024 | 4 | 56,471 |  |  |
| green | 2025 | 4 | 52,132 | 56,471 | -7.70 |
| green | 2026 | 4 | 44,238 | 52,132 | -15.10 |
| green | 2024 | 5 | 61,003 |  |  |
| green | 2025 | 5 | 55,399 | 61,003 | -9.20 |
| green | 2026 | 5 | 44,921 | 55,399 | -18.90 |

**Decision / interpretacion:** green baja todos los meses frente al mismo mes del anio anterior (de -7.0 % a -19.8 %); yellow sube 13-27 % en 2025 y baja 3.5-11.2 % en 2026 (feb-ago). se compara siempre el mismo mes, nunca anio completo contra 2026.

### `sql/03_validacion_anios/v07_filas_vs_ingest_log.sql`

**Objetivo:** la tabla trips debe coincidir con ingest_log (filas por archivo). Devuelve 0 filas si todo cuadra.

**Fuente:** vista `trips` = Parquet de data/raw/{yellow,green}/*/*.parquet normalizados (scripts/taxi_common.py), o la tabla `trips` de taxi.duckdb.

**Consulta SQL:**

```sql
-- Objetivo: la tabla trips debe coincidir con ingest_log (filas por archivo). Devuelve 0 filas si todo cuadra.
-- Requiere: tabla
-- Fuente: vista `trips` = Parquet de data/raw/{yellow,green}/*/*.parquet normalizados (scripts/taxi_common.py), o la tabla `trips` de taxi.duckdb.
-- Decision: 0 filas: trips coincide archivo por archivo con ingest_log.
SELECT l.source_file, l.n_rows AS filas_log, count(t.source_file) AS filas_trips
FROM ingest_log l LEFT JOIN trips t USING (source_file)
GROUP BY l.source_file, l.n_rows
HAVING l.n_rows <> count(t.source_file);
```

**Resultado** (0 filas; se muestran 0; 0.64 s):

| source_file | filas_log | filas_trips |
|---|---|---|

**Decision / interpretacion:** 0 filas: trips coincide archivo por archivo con ingest_log.

### `sql/03_validacion_anios/v08_filas_vs_parquet.sql`

**Objetivo:** contrastar filas de la tabla contra las filas que reporta el footer de cada Parquet (5.6/5.7). Devuelve 0 filas si coinciden. Ejecutar con duckdb desde la raiz del proyecto (ruta /workspace/data en el contenedor).

**Fuente:** vista `trips` = Parquet de data/raw/{yellow,green}/*/*.parquet normalizados (scripts/taxi_common.py), o la tabla `trips` de taxi.duckdb.

**Consulta SQL:**

```sql
-- Objetivo: contrastar filas de la tabla contra las filas que reporta el footer de cada Parquet (5.6/5.7).
-- Devuelve 0 filas si coinciden. Ejecutar con duckdb desde la raiz del proyecto (ruta /workspace/data en el contenedor).
-- Fuente: vista `trips` = Parquet de data/raw/{yellow,green}/*/*.parquet normalizados (scripts/taxi_common.py), o la tabla `trips` de taxi.duckdb.
-- Decision: 0 filas: trips tiene exactamente las filas del footer de cada Parquet, no se perdio ni duplico nada en la carga.
WITH pq AS (
    SELECT regexp_extract(file_name, '[^/\\]+$') AS source_file, num_rows AS filas_parquet
    FROM parquet_file_metadata('/workspace/data/raw/*/*/*.parquet'))
SELECT coalesce(pq.source_file, t.source_file) AS source_file, pq.filas_parquet, t.filas_trips
FROM pq FULL OUTER JOIN (SELECT source_file, count(*) AS filas_trips FROM trips GROUP BY 1) t USING (source_file)
WHERE pq.filas_parquet IS DISTINCT FROM t.filas_trips;
```

**Resultado** (0 filas; se muestran 0; 0.13 s):

| source_file | filas_parquet | filas_trips |
|---|---|---|

**Decision / interpretacion:** 0 filas: trips tiene exactamente las filas del footer de cada Parquet, no se perdio ni duplico nada en la carga.

## Indicadores del tablero (Ej. 7 y 8)

### `sql/05_indicadores/i01_viajes_por_mes_y_tipo.sql`

**Objetivo:** indicador 1, demanda mensual. pregunta: ¿como evoluciona la demanda mes a mes y como se reparte entre yellow y green? justificacion: es la medida base del volumen del servicio y muestra estacionalidad y tendencia. visualizacion: lineas por tipo de taxi.

**Fuente:** tabla `trips` de taxi.duckdb (solo lectura) o vista `trips` sobre los Parquet de data/raw (scripts/taxi_common.py).

**Consulta SQL:**

```sql
-- Objetivo: indicador 1, demanda mensual. pregunta: ¿como evoluciona la demanda mes a mes y como se reparte entre yellow y green? justificacion: es la medida base del volumen del servicio y muestra estacionalidad y tendencia. visualizacion: lineas por tipo de taxi.
-- Fuente: tabla `trips` de taxi.duckdb (solo lectura) o vista `trips` sobre los Parquet de data/raw (scripts/taxi_common.py).
-- Decision: yellow va de 2.96 M viajes (ene 2024) a su maximo de 4.59 M (may 2025) y baja en 2026; green ronda 37 mil a 61 mil por mes y cae. yellow concentra casi toda la demanda; 2026 llega solo hasta agosto.
SELECT date_trunc('month', pickup_datetime)::DATE AS mes, taxi_type, count(*) AS viajes
FROM trips
WHERE pickup_datetime >= TIMESTAMP '2024-01-01' AND pickup_datetime < TIMESTAMP '2027-01-01'
GROUP BY ALL
ORDER BY mes, taxi_type;
```

**Resultado** (64 filas; se muestran 15; 0.65 s):

| mes | taxi_type | viajes |
|---|---|---|
| 2024-01-01 | green | 56,555 |
| 2024-01-01 | yellow | 2,964,617 |
| 2024-02-01 | green | 53,578 |
| 2024-02-01 | yellow | 3,007,533 |
| 2024-03-01 | green | 57,451 |
| 2024-03-01 | yellow | 3,582,611 |
| 2024-04-01 | green | 56,473 |
| 2024-04-01 | yellow | 3,514,295 |
| 2024-05-01 | green | 61,007 |
| 2024-05-01 | yellow | 3,723,843 |
| 2024-06-01 | green | 54,738 |
| 2024-06-01 | yellow | 3,539,170 |
| 2024-07-01 | green | 51,820 |
| 2024-07-01 | yellow | 3,076,876 |
| 2024-08-01 | green | 51,806 |

**Decision / interpretacion:** yellow va de 2.96 M viajes (ene 2024) a su maximo de 4.59 M (may 2025) y baja en 2026; green ronda 37 mil a 61 mil por mes y cae. yellow concentra casi toda la demanda; 2026 llega solo hasta agosto.

### `sql/05_indicadores/i02_ingresos_por_mes_y_tipo.sql`

**Objetivo:** indicador 2, ingresos mensuales. pregunta: ¿cuanto dinero generan los viajes cada mes y que tipo de taxi aporta mas? justificacion: el volumen no basta, el ingreso mezcla viajes y tarifa. se usa total_amount entre 0 y 1000 (como d10) para no sumar montos imposibles. visualizacion: barras apiladas por tipo.

**Fuente:** tabla `trips` de taxi.duckdb (solo lectura) o vista `trips` sobre los Parquet de data/raw (scripts/taxi_common.py).

**Consulta SQL:**

```sql
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
```

**Resultado** (64 filas; se muestran 15; 0.83 s):

| mes | taxi_type | ingresos_millones |
|---|---|---|
| 2024-01-01 | green | 1.27 |
| 2024-01-01 | yellow | 80.33 |
| 2024-02-01 | green | 1.21 |
| 2024-02-01 | yellow | 80.98 |
| 2024-03-01 | green | 1.32 |
| 2024-03-01 | yellow | 98.34 |
| 2024-04-01 | green | 1.32 |
| 2024-04-01 | yellow | 97.81 |
| 2024-05-01 | green | 1.50 |
| 2024-05-01 | yellow | 106.63 |
| 2024-06-01 | green | 1.36 |
| 2024-06-01 | yellow | 100.19 |
| 2024-07-01 | green | 1.29 |
| 2024-07-01 | yellow | 87.88 |
| 2024-08-01 | green | 1.35 |

**Decision / interpretacion:** yellow genera ~99 % del ingreso: 1,162 M (2024), 1,334 M (2025) y 898 M (2026 hasta agosto); green 16.0 M, 14.9 M y 8.6 M. el ingreso sigue la forma del volumen, con un salto de 2024 a 2025 en yellow.

### `sql/05_indicadores/i03_demanda_por_dia_y_hora.sql`

**Objetivo:** indicador 3, patron semanal y horario. pregunta: ¿en que dias y horas se concentra la demanda? justificacion: ayuda a ubicar horas pico y valle y a diferenciar semana de fin de semana. dia_semana: 0 = domingo. suma yellow y green. visualizacion: lineas por dia con la hora en el eje x.

**Fuente:** tabla `trips` de taxi.duckdb (solo lectura) o vista `trips` sobre los Parquet de data/raw (scripts/taxi_common.py).

**Consulta SQL:**

```sql
-- Objetivo: indicador 3, patron semanal y horario. pregunta: ¿en que dias y horas se concentra la demanda? justificacion: ayuda a ubicar horas pico y valle y a diferenciar semana de fin de semana. dia_semana: 0 = domingo. suma yellow y green. visualizacion: lineas por dia con la hora en el eje x.
-- Fuente: tabla `trips` de taxi.duckdb (solo lectura) o vista `trips` sobre los Parquet de data/raw (scripts/taxi_common.py).
-- Decision: pico a las 18 h (8.64 M viajes), luego 17 h y 19 h. el jueves es el dia con mas viajes (18.9 M) y el lunes el de menos (14.8 M). conviene mirar el patron por hora y no solo por dia.
SELECT dayofweek(pickup_datetime) AS dia_semana, dayname(pickup_datetime) AS nombre_dia,
       hour(pickup_datetime) AS hora, count(*) AS viajes
FROM trips
WHERE pickup_datetime >= TIMESTAMP '2024-01-01' AND pickup_datetime < TIMESTAMP '2027-01-01'
GROUP BY ALL
ORDER BY dia_semana, hora;
```

**Resultado** (168 filas; se muestran 15; 0.53 s):

| dia_semana | nombre_dia | hora | viajes |
|---|---|---|---|
| 0 | Sunday | 0 | 1,015,580 |
| 0 | Sunday | 1 | 814,081 |
| 0 | Sunday | 2 | 573,568 |
| 0 | Sunday | 3 | 409,138 |
| 0 | Sunday | 4 | 266,584 |
| 0 | Sunday | 5 | 134,411 |
| 0 | Sunday | 6 | 170,970 |
| 0 | Sunday | 7 | 225,716 |
| 0 | Sunday | 8 | 322,776 |
| 0 | Sunday | 9 | 500,374 |
| 0 | Sunday | 10 | 668,610 |
| 0 | Sunday | 11 | 784,443 |
| 0 | Sunday | 12 | 887,816 |
| 0 | Sunday | 13 | 936,430 |
| 0 | Sunday | 14 | 967,218 |

**Decision / interpretacion:** pico a las 18 h (8.64 M viajes), luego 17 h y 19 h. el jueves es el dia con mas viajes (18.9 M) y el lunes el de menos (14.8 M). conviene mirar el patron por hora y no solo por dia.

### `sql/05_indicadores/i04_pago_y_propina.sql`

**Objetivo:** indicador 4, forma de pago y propina. pregunta: ¿como pagan los pasajeros y cuanta propina dejan segun el pago? justificacion: la propina solo se registra con tarjeta, asi que separar por tipo de pago evita conclusiones falsas. se usan viajes con tarifa entre 1 y 500. visualizacion: barras del porcentaje de viajes y tabla con la propina media.

**Fuente:** tabla `trips` de taxi.duckdb (solo lectura) o vista `trips` sobre los Parquet de data/raw (scripts/taxi_common.py).

**Consulta SQL:**

```sql
-- Objetivo: indicador 4, forma de pago y propina. pregunta: ¿como pagan los pasajeros y cuanta propina dejan segun el pago? justificacion: la propina solo se registra con tarjeta, asi que separar por tipo de pago evita conclusiones falsas. se usan viajes con tarifa entre 1 y 500. visualizacion: barras del porcentaje de viajes y tabla con la propina media.
-- Fuente: tabla `trips` de taxi.duckdb (solo lectura) o vista `trips` sobre los Parquet de data/raw (scripts/taxi_common.py).
-- Decision: yellow: 69.6 % paga con tarjeta (propina media 4.33), 10.8 % en efectivo (0.00) y 18.2 % queda como 'otro o sin dato'. green: 68.6 % tarjeta (3.66) y 23.5 % efectivo. la propina de efectivo no se registra, no es que no haya.
WITH p AS (
    SELECT taxi_type,
           CASE payment_type WHEN 1 THEN 'tarjeta' WHEN 2 THEN 'efectivo'
                             WHEN 3 THEN 'sin cargo' WHEN 4 THEN 'disputa'
                             ELSE 'otro o sin dato' END AS tipo_pago,
           count(*) AS viajes,
           round(avg(tip_amount), 2) AS propina_media
    FROM trips
    WHERE pickup_datetime >= TIMESTAMP '2024-01-01' AND pickup_datetime < TIMESTAMP '2027-01-01'
      AND fare_amount BETWEEN 1 AND 500
    GROUP BY ALL)
SELECT taxi_type, tipo_pago, viajes,
       round(100.0 * viajes / sum(viajes) OVER (PARTITION BY taxi_type), 2) AS pct_viajes,
       propina_media
FROM p
ORDER BY taxi_type, viajes DESC;
```

**Resultado** (10 filas; se muestran 10; 1.08 s):

| taxi_type | tipo_pago | viajes | pct_viajes | propina_media |
|---|---|---|---|---|
| green | tarjeta | 1,080,903 | 68.61 | 3.66 |
| green | efectivo | 370,030 | 23.49 | 0.00 |
| green | otro o sin dato | 116,111 | 7.37 | 1.73 |
| green | sin cargo | 6,270 | 0.40 | 0.05 |
| green | disputa | 2,029 | 0.13 | 0.00 |
| yellow | tarjeta | 80,439,518 | 69.56 | 4.33 |
| yellow | otro o sin dato | 21,092,815 | 18.24 | 0.47 |
| yellow | efectivo | 12,500,531 | 10.81 | 0.00 |
| yellow | disputa | 1,133,448 | 0.98 | 0.01 |
| yellow | sin cargo | 481,559 | 0.42 | 0.01 |

**Decision / interpretacion:** yellow: 69.6 % paga con tarjeta (propina media 4.33), 10.8 % en efectivo (0.00) y 18.2 % queda como 'otro o sin dato'. green: 68.6 % tarjeta (3.66) y 23.5 % efectivo. la propina de efectivo no se registra, no es que no haya.

### `sql/05_indicadores/i05_top_zonas_recogida.sql`

**Objetivo:** indicador 5, zonas de recogida. pregunta: ¿que zonas concentran mas recogidas? justificacion: la zona es la unica variable espacial del conjunto y orienta donde esta la demanda. se muestran ids de zona porque el repositorio no incluye la tabla de nombres. visualizacion: barras horizontales del top 10.

**Fuente:** tabla `trips` de taxi.duckdb (solo lectura) o vista `trips` sobre los Parquet de data/raw (scripts/taxi_common.py).

**Consulta SQL:**

```sql
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
```

**Resultado** (10 filas; se muestran 10; 0.07 s):

| zona | viajes | pct_viajes |
|---|---|---|
| 237 | 5,348,389 | 4.41 |
| 132 | 5,234,789 | 4.32 |
| 161 | 5,227,620 | 4.31 |
| 236 | 4,783,933 | 3.95 |
| 162 | 3,829,301 | 3.16 |
| 186 | 3,809,837 | 3.14 |
| 230 | 3,760,738 | 3.10 |
| 142 | 3,550,483 | 2.93 |
| 138 | 3,328,114 | 2.75 |
| 170 | 3,247,809 | 2.68 |

**Decision / interpretacion:** las zonas 237, 132 y 161 concentran ~4.3-4.4 % de las recogidas cada una; el top 10 suma 34.8 % de los viajes. son ids: para ponerles nombre falta la tabla de zonas de la tlc.

### `sql/05_indicadores/i06_viaje_tipico_por_anio.sql`

**Objetivo:** indicador 6, viaje tipico. pregunta: ¿como es un viaje tipico y cambia de un anio a otro? justificacion: los promedios estan distorsionados por valores imposibles (d01), por eso se usa la mediana sobre viajes plausibles (distancia 0.1-100 millas, tarifa 1-500, duracion 1-180 min). 2026 llega hasta agosto. visualizacion: tabla y barras agrupadas por anio y tipo.

**Fuente:** tabla `trips` de taxi.duckdb (solo lectura) o vista `trips` sobre los Parquet de data/raw (scripts/taxi_common.py).

**Consulta SQL:**

```sql
-- Objetivo: indicador 6, viaje tipico. pregunta: ¿como es un viaje tipico y cambia de un anio a otro? justificacion: los promedios estan distorsionados por valores imposibles (d01), por eso se usa la mediana sobre viajes plausibles (distancia 0.1-100 millas, tarifa 1-500, duracion 1-180 min). 2026 llega hasta agosto. visualizacion: tabla y barras agrupadas por anio y tipo.
-- Fuente: tabla `trips` de taxi.duckdb (solo lectura) o vista `trips` sobre los Parquet de data/raw (scripts/taxi_common.py).
-- Decision: el viaje tipico se alarga poco a poco: yellow pasa de 1.80 a 1.95 millas y de 13.1 a 14.1 min (2024 a 2026); green de 1.99 a 2.15 millas y de 12.1 a 13.3 min. la tarifa mediana de yellow sube de 14.20 a 15.60 solo en 2026; la de green se mantiene en 13.50.
WITH v AS (
    SELECT taxi_type, year(pickup_datetime) AS anio, trip_distance, fare_amount,
           date_diff('second', pickup_datetime, dropoff_datetime) / 60.0 AS minutos
    FROM trips
    WHERE pickup_datetime >= TIMESTAMP '2024-01-01' AND pickup_datetime < TIMESTAMP '2027-01-01'
      AND dropoff_datetime > pickup_datetime
      AND trip_distance BETWEEN 0.1 AND 100
      AND fare_amount BETWEEN 1 AND 500)
SELECT taxi_type, anio, count(*) AS viajes,
       round(median(trip_distance), 2) AS distancia_mediana_millas,
       round(median(minutos), 1) AS duracion_mediana_min,
       round(median(fare_amount), 2) AS tarifa_mediana
FROM v
WHERE minutos BETWEEN 1 AND 180
GROUP BY taxi_type, anio
ORDER BY taxi_type, anio;
```

**Resultado** (6 filas; se muestran 6; 28.51 s):

| taxi_type | anio | viajes | distancia_mediana_millas | duracion_mediana_min | tarifa_mediana |
|---|---|---|---|---|---|
| green | 2024 | 612,744 | 1.99 | 12.10 | 13.50 |
| green | 2025 | 550,481 | 2.08 | 12.80 | 13.50 |
| green | 2026 | 313,989 | 2.15 | 13.30 | 13.50 |
| yellow | 2024 | 39,461,705 | 1.80 | 13.10 | 14.20 |
| yellow | 2025 | 43,726,788 | 1.90 | 13.60 | 14.20 |
| yellow | 2026 | 27,971,632 | 1.95 | 14.10 | 15.60 |

**Decision / interpretacion:** el viaje tipico se alarga poco a poco: yellow pasa de 1.80 a 1.95 millas y de 13.1 a 14.1 min (2024 a 2026); green de 1.99 a 2.15 millas y de 12.1 a 13.3 min. la tarifa mediana de yellow sube de 14.20 a 15.60 solo en 2026; la de green se mantiene en 13.50.

### `sql/05_indicadores/i07_variacion_interanual.sql`

**Objetivo:** indicador 7, variacion interanual. pregunta: ¿crece o cae la demanda frente al mismo mes del anio anterior? justificacion: comparar el mismo mes elimina la estacionalidad y no mezcla un 2026 incompleto con anios completos. visualizacion: barras de variacion porcentual por mes y tipo.

**Fuente:** tabla `trips` de taxi.duckdb (solo lectura) o vista `trips` sobre los Parquet de data/raw (scripts/taxi_common.py).

**Consulta SQL:**

```sql
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
```

**Resultado** (40 filas; se muestran 15; 11.62 s):

| taxi_type | mes | viajes | viajes_anio_anterior | variacion_pct |
|---|---|---|---|---|
| green | 2025-01-01 | 48,299 | 56,555 | -14.60 |
| green | 2025-02-01 | 46,645 | 53,578 | -12.90 |
| green | 2025-03-01 | 51,550 | 57,451 | -10.30 |
| green | 2025-04-01 | 52,134 | 56,473 | -7.70 |
| green | 2025-05-01 | 55,405 | 61,007 | -9.20 |
| green | 2025-06-01 | 49,385 | 54,738 | -9.80 |
| green | 2025-07-01 | 48,202 | 51,820 | -7.00 |
| green | 2025-08-01 | 46,305 | 51,806 | -10.60 |
| green | 2025-09-01 | 48,885 | 54,422 | -10.20 |
| green | 2025-10-01 | 49,417 | 56,153 | -12.00 |
| green | 2025-11-01 | 46,915 | 52,214 | -10.10 |
| green | 2025-12-01 | 48,227 | 53,987 | -10.70 |
| green | 2026-01-01 | 40,272 | 48,299 | -16.60 |
| green | 2026-02-01 | 37,388 | 46,645 | -19.80 |
| green | 2026-03-01 | 44,203 | 51,550 | -14.30 |

**Decision / interpretacion:** green cae todos los meses (de -7.0 % a -14.6 % en 2025 y de -10.6 % a -19.8 % en 2026); yellow sube de +13.0 % a +26.7 % en 2025 y en 2026 va de -11.2 % a +7.2 %. se compara siempre el mismo mes.

### `sql/05_indicadores/i08_calidad_por_anio_y_tipo.sql`

**Objetivo:** indicador 8, calidad de datos. pregunta: ¿que proporcion de los registros es inconsistente y mejora o empeora por anio? justificacion: cualquier indicador depende de la calidad del dato; mide cuanto se descarta con los filtros del analisis. se agrupa por anio del archivo (source_year). visualizacion: barras por anio y tipo.

**Fuente:** tabla `trips` de taxi.duckdb (solo lectura) o vista `trips` sobre los Parquet de data/raw (scripts/taxi_common.py).

**Consulta SQL:**

```sql
-- Objetivo: indicador 8, calidad de datos. pregunta: ¿que proporcion de los registros es inconsistente y mejora o empeora por anio? justificacion: cualquier indicador depende de la calidad del dato; mide cuanto se descarta con los filtros del analisis. se agrupa por anio del archivo (source_year). visualizacion: barras por anio y tipo.
-- Fuente: tabla `trips` de taxi.duckdb (solo lectura) o vista `trips` sobre los Parquet de data/raw (scripts/taxi_common.py).
-- Decision: yellow 2025 tiene 9.58 % de registros inconsistentes contra 3.71 % en 2024 y 5.00 % en 2026, por tarifas negativas (2.85 M, el 5.8 % del anio; 72 % de las tarifas < 1 de ese anio son de payment_type 0). green se mantiene entre 5.5 % y 6.0 %. no se corrige trips: se filtra en cada indicador.
SELECT taxi_type, source_year AS anio, count(*) AS viajes,
       round(100.0 * count_if(trip_distance <= 0 OR trip_distance > 100) / count(*), 2) AS pct_distancia_invalida,
       round(100.0 * count_if(fare_amount < 1 OR fare_amount > 500) / count(*), 2) AS pct_tarifa_invalida,
       round(100.0 * count_if(dropoff_datetime <= pickup_datetime
                              OR dropoff_datetime - pickup_datetime > INTERVAL 3 HOUR) / count(*), 2) AS pct_duracion_invalida,
       round(100.0 * count_if(trip_distance <= 0 OR trip_distance > 100
                              OR fare_amount < 1 OR fare_amount > 500
                              OR dropoff_datetime <= pickup_datetime
                              OR dropoff_datetime - pickup_datetime > INTERVAL 3 HOUR) / count(*), 2) AS pct_alguna
FROM trips
GROUP BY taxi_type, source_year
ORDER BY taxi_type, anio;
```

**Resultado** (6 filas; se muestran 6; 3.85 s):

| taxi_type | anio | viajes | pct_distancia_invalida | pct_tarifa_invalida | pct_duracion_invalida | pct_alguna |
|---|---|---|---|---|---|---|
| green | 2024 | 660,218 | 5.27 | 0.43 | 0.55 | 5.97 |
| green | 2025 | 591,375 | 4.17 | 0.77 | 0.78 | 5.47 |
| green | 2026 | 337,114 | 3.64 | 1.77 | 0.45 | 5.62 |
| yellow | 2024 | 41,169,720 | 1.89 | 1.91 | 0.09 | 3.71 |
| yellow | 2025 | 48,722,602 | 2.89 | 6.11 | 1.16 | 9.58 |
| yellow | 2026 | 29,703,355 | 3.21 | 0.61 | 1.29 | 5.00 |

**Decision / interpretacion:** yellow 2025 tiene 9.58 % de registros inconsistentes contra 3.71 % en 2024 y 5.00 % en 2026, por tarifas negativas (2.85 M, el 5.8 % del anio; 72 % de las tarifas < 1 de ese anio son de payment_type 0). green se mantiene entre 5.5 % y 6.0 %. no se corrige trips: se filtra en cada indicador.

