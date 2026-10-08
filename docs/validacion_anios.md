# Ejercicios 5.6 - 5.8 y 8.3 - Validacion al incorporar anios

Consultas: `sql/03_validacion_anios/`. Notebook: `notebooks/03_validacion_y_benchmark.ipynb`.

## 5.6 Consulta conjunta de 2024 y 2026

`v00_consulta_conjunta_parquet.sql` lee `data/raw/*/*/*.parquet` con `union_by_name=true` y muestra archivos, registros y rango de fechas por tipo y anio: si aparecen 2024, 2025 y 2026 en una sola consulta, los anios se pueden consultar juntos. Complementan `v01` (filas por archivo) y `v02` (huecos de meses).

## 5.7 ¿Hubo que modificar las consultas anteriores?

**No.** Las consultas de `sql/01_exploracion` y `sql/02_eda` no mencionan ningun anio en la ruta: usan comodines (`data/raw/yellow/*/*.parquet`) o la vista `trips`, que se construye con el mismo comodin en `scripts/taxi_common.py`. Al llegar archivos de 2024 y 2025 solo cambia **cuantos** archivos cubre el comodin.

Como comprobarlo (comprobacion automatica):

```bash
# con solo 2026 descargado
docker compose exec lab python scripts/document_queries.py --out docs/consultas_resultados_2026.md
# despues de descargar 2024 y 2025: el mismo comando, sin tocar ninguna consulta
docker compose exec lab python scripts/document_queries.py
```

Ambas ejecuciones deben terminar con `fallas: 0`. El script termina con codigo 1 si alguna consulta falla, y la tabla "Resumen de ejecucion" de la salida es la evidencia.

Solo hay **una excepcion intencional**: las consultas que usan una fecha de corte fija (`d05`, `d10` filtran `2024-01-01` a `2027-01-01` para excluir fechas imposibles). Si se agregara un anio fuera de ese rango (por ejemplo 2027), hay que ampliar ese filtro; esta documentado aqui y en su comentario.

Resultado de ejecutar `document_queries.py`, sin modificar ninguna consulta, con tres conjuntos de datos (2026-10-08). Entre parentesis, el numero de filas del resultado.

- **Solo 2026** (16 archivos, copia temporal en `LAB_DATA_DIR`, ya eliminada), leyendo Parquet: 39 consultas ejecutadas, 1 omitidas (requieren la tabla), **0 fallas**.
- **2024-2026** (64 archivos), leyendo Parquet: 39 ejecutadas, 1 omitidas, **0 fallas**.
- **2024-2026**, sobre la tabla materializada: 40 ejecutadas, 0 omitidas, **0 fallas**.

Que cambie el numero de filas entre columnas es lo esperado (hay mas meses y años); `i07` devuelve 0 filas con solo 2026 porque no existe un año anterior con que comparar, y `v07` solo se ejecuta contra la tabla.

| Consulta | Solo 2026, Parquet | 2024-2026, Parquet | 2024-2026, tabla |
|---|---|---|---|
| `01_exploracion/p01_archivos.sql` | OK (5) | OK (9) | OK (9) |
| `01_exploracion/p02_registros.sql` | OK (5) | OK (9) | OK (9) |
| `01_exploracion/p03_columnas_tipos_yellow.sql` | OK (21) | OK (21) | OK (21) |
| `01_exploracion/p04_columnas_tipos_green.sql` | OK (22) | OK (22) | OK (22) |
| `01_exploracion/p05_comparar_columnas.sql` | OK (25) | OK (25) | OK (25) |
| `01_exploracion/p06_cambios_de_tipo_entre_archivos.sql` | OK (0) | OK (0) | OK (0) |
| `01_exploracion/p07_columnas_por_archivo.sql` | OK (2) | OK (4) | OK (4) |
| `01_exploracion/p08_muestra.sql` | OK (10) | OK (10) | OK (10) |
| `01_exploracion/p09_resumen_yellow.sql` | OK (21) | OK (21) | OK (21) |
| `01_exploracion/p10_resumen_green.sql` | OK (22) | OK (22) | OK (22) |
| `01_exploracion/p11_calidad_conteos.sql` | OK (2) | OK (2) | OK (2) |
| `01_exploracion/p12_fechas_fuera_de_rango.sql` | OK (9) | OK (15) | OK (15) |
| `02_eda/d01_estadisticos_numericos.sql` | OK (2) | OK (2) | OK (2) |
| `02_eda/d02_calidad_datos.sql` | OK (2) | OK (2) | OK (2) |
| `02_eda/d03_distribucion_distancia.sql` | OK (14) | OK (14) | OK (14) |
| `02_eda/d04_duracion_y_velocidad.sql` | OK (2) | OK (2) | OK (2) |
| `02_eda/d05_patron_hora_dia.sql` | OK (336) | OK (336) | OK (336) |
| `02_eda/d06_pago_y_propinas.sql` | OK (11) | OK (12) | OK (12) |
| `02_eda/d07_zonas_recogida_destino.sql` | OK (25) | OK (25) | OK (25) |
| `02_eda/d08_correlaciones.sql` | OK (2) | OK (2) | OK (2) |
| `02_eda/d09_atipicos_iqr.sql` | OK (2) | OK (2) | OK (2) |
| `02_eda/d10_tendencia_mensual.sql` | OK (18) | OK (64) | OK (64) |
| `02_eda/d11_comparacion_yellow_green.sql` | OK (2) | OK (2) | OK (2) |
| `03_validacion_anios/v00_consulta_conjunta_parquet.sql` | OK (2) | OK (6) | OK (6) |
| `03_validacion_anios/v01_viajes_por_anio_mes.sql` | OK (8) | OK (32) | OK (32) |
| `03_validacion_anios/v02_meses_faltantes.sql` | OK (0) | OK (0) | OK (0) |
| `03_validacion_anios/v03_fechas_fuera_de_su_archivo.sql` | OK (16) | OK (30) | OK (30) |
| `03_validacion_anios/v04_columnas_por_anio.sql` | OK (2) | OK (6) | OK (6) |
| `03_validacion_anios/v05_metricas_por_anio.sql` | OK (2) | OK (6) | OK (6) |
| `03_validacion_anios/v06_comparacion_mismo_mes.sql` | OK (16) | OK (64) | OK (64) |
| `03_validacion_anios/v07_filas_vs_ingest_log.sql` | omitida | omitida | OK (0) |
| `03_validacion_anios/v08_filas_vs_parquet.sql` | OK (0) | OK (0) | OK (0) |
| `05_indicadores/i01_viajes_por_mes_y_tipo.sql` | OK (18) | OK (64) | OK (64) |
| `05_indicadores/i02_ingresos_por_mes_y_tipo.sql` | OK (18) | OK (64) | OK (64) |
| `05_indicadores/i03_demanda_por_dia_y_hora.sql` | OK (168) | OK (168) | OK (168) |
| `05_indicadores/i04_pago_y_propina.sql` | OK (10) | OK (10) | OK (10) |
| `05_indicadores/i05_top_zonas_recogida.sql` | OK (10) | OK (10) | OK (10) |
| `05_indicadores/i06_viaje_tipico_por_anio.sql` | OK (4) | OK (6) | OK (6) |
| `05_indicadores/i07_variacion_interanual.sql` | OK (0) | OK (40) | OK (40) |
| `05_indicadores/i08_calidad_por_anio_y_tipo.sql` | OK (2) | OK (6) | OK (6) |


## 5.8 Consultas usadas para validar 2024

| Consulta | Que valida |
|---|---|
| `v00` | Los tres anios se leen juntos directamente desde Parquet. |
| `v01` | Cada archivo mensual aporta filas. |
| `v02` | No hay meses intermedios faltantes. |
| `v03` | Cuantos viajes tienen fecha fuera del mes de su archivo. |
| `v04` | Columnas que cambian entre anios (`cbd_congestion_fee`, `airport_fee`, ...). |
| `v05`, `v06` | Que las metricas y el volumen por anio sean coherentes (no hay cambios bruscos sin explicacion). |
| `v07`, `v08` | Que la tabla materializada tenga exactamente las filas de los Parquet y de `ingest_log`. |

## 8.3 Conjunto ampliado (2024, 2025, 2026)

Mismo procedimiento que 5.7: `document_queries.py` con los tres anios y con `--source tabla`; ambos deben dar `fallas: 0` y `v07`/`v08` deben devolver 0 filas.

## 8.4 Indicadores y visualizaciones con los tres años

Los 8 indicadores (`sql/05_indicadores/`) y el dashboard de Metabase se construyeron directamente sobre la base con 2024, 2025 y 2026 (64 archivos, 121,184,384 viajes); no hubo una version previa solo con 2026. Las consultas no nombran años: filtran la fecha de recogida entre 2024-01-01 y 2027-01-01 (el mismo criterio de `d05` y `d10`). Evidencia visual en `docs/tablero/`.

## 8.5 Evolucion de los indicadores en el tiempo

| Indicador | 2024 | 2025 | 2026 (hasta agosto) |
|---|---|---|---|
| I1 viajes yellow, minimo y maximo mensual | 2.96 M (ene) | 4.59 M (may, maximo de todo el periodo) | 3.34 M (ago) |
| I2 ingresos yellow (USD) | 1,162.1 M | 1,334.1 M | 897.8 M |
| I2 ingresos green (USD) | 16.0 M | 14.9 M | 8.6 M |
| I6 mediana de distancia, yellow | 1.80 mi | 1.90 mi | 1.95 mi |
| I6 mediana de duracion, yellow | 13.1 min | 13.6 min | 14.1 min |
| I6 tarifa mediana, yellow | 14.20 | 14.20 | 15.60 |
| I7 variacion interanual de viajes, yellow | (base) | +13.0 % a +26.7 % | -11.2 % a +7.2 % |
| I7 variacion interanual de viajes, green | (base) | -14.6 % a -7.0 % | -19.8 % a -10.6 % |
| I8 registros inconsistentes, yellow | 3.71 % | 9.58 % | 5.00 % |
| I8 registros inconsistentes, green | 5.97 % | 5.47 % | 5.62 % |

## 8.6 Cambios o patrones visibles al considerar 2024, 2025 y 2026

1. **Yellow crece en 2025 y retrocede en 2026, pero el ingreso mensual no baja.** Los viajes suben entre 13.0 % y 26.7 % en 2025 y en 2026 varian entre -11.2 % y +7.2 % (`i07`). Aun asi, el ingreso mensual medio es 112.2 M en 2026 (897.8 M en 8 meses) contra 111.2 M en 2025 (1,334.1 M en 12) y 96.8 M en 2024: menos viajes, con tarifa mediana mas alta (15.60 frente a 14.20) (`i02`, `i06`).
2. **Green cae de forma sostenida:** baja todos los meses frente al mismo mes del año anterior, de -7.0 % a -14.6 % en 2025 y de -10.6 % a -19.8 % en 2026 (`i07`). En 2024 tenia ~56 mil viajes en enero y en 2026 ~40 mil.
3. **El viaje tipico se alarga poco a poco** en ambos tipos: yellow de 1.80 a 1.95 millas y de 13.1 a 14.1 min; green de 1.99 a 2.15 millas y de 12.1 a 13.3 min (`i06`).
4. **La calidad del dato no es estable:** yellow 2025 tiene 9.58 % de registros inconsistentes frente a 3.71 % en 2024 y 5.00 % en 2026, por 2.85 M de tarifas negativas en 2025 (`i08`).
5. **El esquema cambia:** `cbd_congestion_fee` es 0 % en 2024 y ~100 % desde 2025; `airport_fee` en yellow baja de 90.1 % a 76.2 % y 74.0 % (`v04`).

Advertencia: 2026 llega solo hasta agosto (septiembre a diciembre aun no estan publicados), por eso se comparan meses iguales y no años completos.

## 8.7 Consultas utilizadas

- Validacion de los años: `sql/03_validacion_anios/v00` a `v08` (resultados en `docs/consultas_resultados.md`).
- Resultados del analisis: `sql/05_indicadores/i01` a `i08`, mas `sql/02_eda/d10` (tendencia mensual) y `d02` (calidad).
- Indice completo con objetivo de cada una: `docs/consultas.md`. Resultado, tiempo y decision de cada consulta: `docs/consultas_resultados.md`.

