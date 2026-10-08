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

<!-- COMPLETAR: pegar la tabla "Resumen de ejecucion" de ambas corridas como evidencia. -->

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
