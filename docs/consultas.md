# Documentacion de las consultas SQL

Indice de todas las consultas. **La documentacion completa de cada una (consulta, objetivo, fuente, resultado obtenido y decision)** se genera con:

```bash
docker compose exec lab python scripts/document_queries.py                  # lee los Parquet directamente
docker compose exec lab python scripts/document_queries.py --source tabla    # usa la tabla materializada
```

El resultado queda en `docs/consultas_resultados.md`. La **decision** de cada consulta se escribe en su archivo `.sql` como comentario `-- Decision: ...` y se vuelve a ejecutar el script. Un `.sql` sin `-- Decision:` aparece como _PENDIENTE_ en el documento.

## Convenciones

- Cada `.sql` empieza con comentarios `-- Objetivo:` y `-- Fuente:` (este indice se construye a partir de ellos).
- La vista `trips` une yellow y green con esquema normalizado (`scripts/taxi_common.py`). **No se filtra ni corrige nada al cargar**: los filtros de calidad (distancia 0.1-100 millas, tarifa 1-500, duracion 1-180 min) se aplican dentro de cada consulta y se declaran en su objetivo.
- `taxi_type` distingue `yellow` y `green`; `source_year`/`source_month` salen del nombre del archivo y `pickup_datetime` de la fecha real del viaje (pueden diferir; ver `v03`).
- `dayofweek`: 0 = domingo. `payment_type`: 1 tarjeta, 2 efectivo, 3 sin cargo, 4 disputa.
- Las rutas `/workspace/data` son las del contenedor; `document_queries.py` y los notebooks las ajustan si se ejecutan fuera de el.
- Las consultas **no mencionan anios** en las rutas, por lo que no cambian al incorporar 2024 y 2025 (ver `docs/validacion_anios.md`).

## Exploracion con Parquet directo (Ej. 3)

Carpeta `sql/01_exploracion/` | Se ejecuta desde: `notebooks/01_exploracion.ipynb` | Leen los archivos con `read_parquet` / `glob` / `parquet_schema`, sin tabla.

| Archivo | Objetivo |
|---|---|
| `p01_archivos.sql` | 3.1 cantidad de archivos Parquet disponibles, por tipo de taxi y anio (con subtotales y total). |
| `p02_registros.sql` | 3.2 cantidad de registros disponibles, por tipo de taxi y anio de archivo (con subtotales y total). |
| `p03_columnas_tipos_yellow.sql` | 3.3 y 3.4 columnas y tipos de datos de los archivos de taxis amarillos (esquema unificado de todos los archivos). |
| `p04_columnas_tipos_green.sql` | 3.3 y 3.4 columnas y tipos de datos de los archivos de taxis verdes (esquema unificado de todos los archivos). |
| `p05_comparar_columnas.sql` | 3.3 comparar las columnas de yellow y green (cuales son comunes, cuales exclusivas y si cambia el tipo). |
| `p06_cambios_de_tipo_entre_archivos.sql` | 3.4 / 3.6 detectar columnas cuyo tipo fisico en Parquet cambia de un archivo a otro (riesgo al combinar archivos). |
| `p07_columnas_por_archivo.sql` | 3.3 / 3.6 columnas que NO estan presentes en todos los archivos de un tipo (esquema que evoluciona entre meses/anios). |
| `p08_muestra.sql` | 3.5 muestra aleatoria de registros de cada tipo de taxi (las columnas exclusivas de un tipo quedan en NULL en el otro). |
| `p09_resumen_yellow.sql` | 3.6 perfil estadistico de cada columna de yellow (minimo, maximo, cuartiles, % de nulos): permite ver valores imposibles. |
| `p10_resumen_green.sql` | 3.6 perfil estadistico de cada columna de green (minimo, maximo, cuartiles, % de nulos): permite ver valores imposibles. |
| `p11_calidad_conteos.sql` | 3.6 cuantificar registros problematicos por tipo de taxi (fechas, duraciones, distancias, tarifas, pasajeros, zonas). |
| `p12_fechas_fuera_de_rango.sql` | 3.6 distribucion de los anios de recogida por tipo: revela fechas imposibles (p. ej. 2002 o 2009) dentro de archivos de 2024-2026. |

## Analisis exploratorio (Ej. 4)

Carpeta `sql/02_eda/` | Se ejecuta desde: `notebooks/02_eda.ipynb` | Usan la vista `trips` (yellow + green normalizados).

| Archivo | Objetivo |
|---|---|
| `d01_estadisticos_numericos.sql` | estadisticos descriptivos de las variables numericas clave por tipo de taxi. |
| `d02_calidad_datos.sql` | cuantificar problemas de calidad (registros sospechosos) por tipo de taxi. |
| `d03_distribucion_distancia.sql` | histograma de distancia de viaje (millas) para ver forma de la distribucion y cola larga. |
| `d04_duracion_y_velocidad.sql` | duracion y velocidad promedio, usando solo viajes plausibles (1 min a 3 h, distancia > 0). |
| `d05_patron_hora_dia.sql` | demanda por dia de la semana (0 = domingo) y hora; sirve para un mapa de calor. |
| `d06_pago_y_propinas.sql` | metodo de pago y propinas. La propina solo se registra de forma confiable con tarjeta (payment_type = 1). |
| `d07_zonas_recogida_destino.sql` | zonas mas activas como origen y como destino (IDs de zona de la TLC; sin tabla de nombres en el repo). |
| `d08_correlaciones.sql` | correlacion entre variables numericas (viajes con valores positivos y plausibles). |
| `d09_atipicos_iqr.sql` | valores atipicos de tarifa con el criterio del rango intercuartil (IQR), por tipo de taxi. |
| `d10_tendencia_mensual.sql` | comportamiento temporal. Viajes e ingresos por mes de recogida y tipo de taxi (tendencia y estacionalidad). |
| `d11_comparacion_yellow_green.sql` | diferencias entre taxis amarillos y verdes en una sola tabla (volumen, distancia, duracion, tarifa, propina, pasajeros, tarjeta). Solo viajes plausibles: distancia 0.1-100 millas, tarifa 1-500, duracion 1-180 minutos. |

## Validacion al incorporar anios (Ej. 5 y 8.3)

Carpeta `sql/03_validacion_anios/` | Se ejecuta desde: `notebooks/03_validacion_y_benchmark.ipynb` | `v00` y `v08` leen Parquet directo; el resto usa la vista `trips`; `v07` requiere la tabla.

| Archivo | Objetivo |
|---|---|
| `v00_consulta_conjunta_parquet.sql` | 5.6 comprobar, leyendo directamente los Parquet con un comodin, que se pueden consultar juntos 2024, 2025 y 2026 (archivos, registros y rango de fechas por anio y tipo). Sin tabla materializada. |
| `v01_viajes_por_anio_mes.sql` | confirmar que cada archivo mensual aporta filas (conteo por anio, mes y tipo segun el ARCHIVO de origen). |
| `v02_meses_faltantes.sql` | detectar meses sin archivo entre el primero y el ultimo cargado, por tipo de taxi. Un mes final ausente puede ser normal (la TLC publica con atraso); un hueco intermedio no. |
| `v03_fechas_fuera_de_su_archivo.sql` | viajes cuya fecha de recogida no corresponde al mes del archivo (error de captura o de la fuente). |
| `v04_columnas_por_anio.sql` | % de filas NO nulas de las columnas que cambian entre anios (esquema evolutivo). cbd_congestion_fee aparece desde 2025; airport_fee solo en yellow; ehail_fee/trip_type solo en green. |
| `v05_metricas_por_anio.sql` | comparar metricas clave entre anios para detectar cambios bruscos o inconsistencias (solo viajes plausibles). |
| `v06_comparacion_mismo_mes.sql` | variacion interanual de viajes comparando el mismo mes entre anios consecutivos. |
| `v07_filas_vs_ingest_log.sql` | la tabla trips debe coincidir con ingest_log (filas por archivo). Devuelve 0 filas si todo cuadra. |
| `v08_filas_vs_parquet.sql` | contrastar filas de la tabla contra las filas que reporta el footer de cada Parquet (5.6/5.7). Devuelve 0 filas si coinciden. Ejecutar con duckdb desde la raiz del proyecto (ruta /workspace/data en el contenedor). |

## Benchmark (Ej. 6)

Carpeta `sql/04_benchmark/` | Se ejecuta desde: `scripts/benchmark.py` | Usan `trips` como Parquet y como tabla; ver `docs/benchmark.md`.

| Archivo | Objetivo |
|---|---|
| `q01_conteo_total.sql` | conteo total de viajes (escaneo minimo; en Parquet puede resolverse con metadatos). |
| `q02_viajes_por_mes_y_tipo.sql` | comportamiento temporal. Viajes por mes y tipo de taxi (agregacion con 2 columnas). |
| `q03_tarifas_por_tipo_pago.sql` | variables de pago. Promedios de tarifa, propina y total por tipo de taxi y metodo de pago. |
| `q04_top_zonas_recogida.sql` | caracteristicas de los viajes. Las 20 zonas de recogida con mas viajes (GROUP BY + TOP-N). |
| `q05_perfil_dia_hora.sql` | patron temporal. Viajes y total promedio por dia de la semana y hora (funciones sobre timestamp). |
| `q06_filtro_selectivo_atipicos.sql` | valores atipicos. Filtro muy selectivo (pocas filas cumplen); favorece pruning y estadisticas por columna. |
| `q07_escaneo_multiples_columnas.sql` | escaneo de muchas columnas numericas (peor caso para formato columnar: se leen casi todas). |
| `q08_mediana_y_percentil.sql` | distribucion de valores. Mediana del total y percentil 95 de la distancia (agregados que requieren ordenar). |

## Indicadores y tablero (Ej. 7 y 8)

Carpeta `sql/05_indicadores/` | Se carga en Metabase con `scripts/metabase_setup.py` | Se documenta con `scripts/document_queries.py` (resultado, tiempo y decision de cada uno en `docs/consultas_resultados.md`) | Evidencia visual en `docs/tablero/`.

### 7.1 Preguntas de analisis y su indicador

| # | Pregunta | Indicador |
|---|---|---|
| 1 | ¿Como evoluciona la demanda mes a mes? | I1 |
| 2 | ¿Que parte de la demanda corresponde a yellow y a green? | I1, I2 |
| 3 | ¿Cuanto dinero generan los viajes cada mes? | I2 |
| 4 | ¿A que horas se concentra la demanda? | I3 |
| 5 | ¿Que dias de la semana hay mas y menos viajes? | I3 |
| 6 | ¿Como pagan los pasajeros? | I4 |
| 7 | ¿Cuanta propina se deja segun la forma de pago? | I4 |
| 8 | ¿Que zonas concentran mas recogidas? | I5 |
| 9 | ¿Como es un viaje tipico y cambia de un anio a otro? | I6 |
| 10 | ¿Crece o cae la demanda frente al mismo mes del anio anterior? | I7 |
| 11 | ¿Que proporcion de los registros es inconsistente? | I8 |

### 7.2 a 7.7 Indicadores, consulta, visualizacion y justificacion

La pregunta, la justificacion y la visualizacion de cada indicador estan en el `-- Objetivo:` de su `.sql`; la interpretacion, en su `-- Decision:`.

| Indicador | Archivo | Visualizacion |
|---|---|---|
| I1 Viajes por mes y tipo | `i01_viajes_por_mes_y_tipo.sql` | Lineas, green en eje derecho |
| I2 Ingresos por mes | `i02_ingresos_por_mes_y_tipo.sql` | Barras apiladas |
| I3 Demanda por hora y dia | `i03_demanda_por_dia_y_hora.sql` | Lineas por dia de la semana |
| I4 Forma de pago y propina | `i04_pago_y_propina.sql` | Barras (% de viajes) |
| I5 Top 10 zonas de recogida | `i05_top_zonas_recogida.sql` | Barras horizontales |
| I6 Viaje tipico por anio | `i06_viaje_tipico_por_anio.sql` | Tabla de medianas |
| I7 Variacion interanual | `i07_variacion_interanual.sql` | Barras de variacion % |
| I8 Calidad de datos | `i08_calidad_por_anio_y_tipo.sql` | Barras por anio y tipo |

### 7.8 Principales hallazgos del tablero

- **Yellow domina:** ~99 % del ingreso (1,162 M, 1,334 M y 898 M de USD en 2024, 2025 y 2026 hasta agosto) frente a 16.0 M, 14.9 M y 8.6 M de green (`i02`).
- **Horario:** pico a las 18 h (8.64 M viajes); el jueves es el dia con mas viajes y el lunes el de menos (`i03`).
- **Pago:** ~69 % de los viajes paga con tarjeta y solo ahi hay propina registrada (4.33 en yellow, 3.66 en green) (`i04`).
- **Tendencia:** green cae todos los meses frente al mismo mes del anio anterior; yellow sube hasta 26.7 % en 2025 y baja hasta 11.2 % en 2026 (`i07`).
- **Calidad:** yellow 2025 tiene 9.58 % de registros inconsistentes contra 3.71 % en 2024, por tarifas negativas (`i08`).
- Limitacion: las zonas se muestran por id (no hay tabla de nombres) y 2026 llega solo hasta agosto.

## Documentos asociados

- `docs/exploracion.md`: Ej. 3 (3.6 calidad de datos y 3.9).
- `docs/eda.md`: Ej. 4 (preguntas 4.1 y hallazgos 4.5).
- `docs/validacion_anios.md`: 5.6 a 5.8 y 8.3 a 8.7.
- `docs/benchmark_analisis.md`: 6.9 y 6.10.
- `docs/discusion_B.md`: 9.1 a 9.8.
- `docs/tablero/`: capturas del dashboard y de cada indicador.
