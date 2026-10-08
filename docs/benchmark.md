# Benchmark: Parquet directo vs tabla materializada en DuckDB (Ejercicio 6)

Scripts: `scripts/build_db.py` (6.2), `scripts/benchmark.py` (6.1, 6.4–6.7).
Consultas: `sql/04_benchmark/q*.sql` (6.3, 6.8). Resultados generados: `docs/benchmark_results.csv` y `docs/benchmark_results.md` (6.7).

## Diseño de la comparación (para que sea válida)

- **Mismas consultas, mismo esquema.** Ambas estrategias exponen una relación `trips` con las mismas columnas y tipos,
  generada por la **misma sentencia SQL normalizada** (`scripts/taxi_common.py`). Para Parquet es una vista temporal que lee los
  archivos; para la tabla es una vista sobre `trips` de `data/processed/taxi.duckdb`. Los archivos `q*.sql` se ejecutan sin cambios en ambos casos.
- **Equivalencia comprobada.** El script compara los resultados de ambas estrategias (tolerancia relativa 1e-6) y lo registra en la columna `resultado_equivalente`.
- **Distintas cantidades de datos (6.6).** Escalas de 1, 3, 6, 12, 24 meses y todo el conjunto (primeros N meses cronológicos, yellow + green).
- **Medición.** Cada consulta se ejecuta 5 veces; se registra la primera ejecución, la mediana y el mínimo. El tiempo incluye traer todo el resultado (`fetchall`).
- **Aislamiento.** Cada estrategia usa su propia conexión y se ejecutan una después de otra.
- **Escritor único.** La base se abre en modo de solo lectura durante el benchmark.

## Consultas utilizadas (6.8)

| Consulta | Qué ejercita |
|---|---|
| `q01_conteo_total` | Conteo total; en Parquet puede resolverse casi solo con metadatos. |
| `q02_viajes_por_mes_y_tipo` | Agregación temporal con `date_trunc`. |
| `q03_tarifas_por_tipo_pago` | Agregaciones sobre variables de pago. |
| `q04_top_zonas_recogida` | `GROUP BY` con Top-N. |
| `q05_perfil_dia_hora` | Funciones sobre timestamp, agrupación por día y hora. |
| `q06_filtro_selectivo_atipicos` | Filtro muy selectivo (aprovecha estadísticas por columna). |
| `q07_escaneo_multiples_columnas` | Lee casi todas las columnas numéricas. |
| `q08_mediana_y_percentil` | Agregados que requieren ordenar (mediana, percentil 95). |

Cada archivo `.sql` incluye su objetivo como comentario.

## Cómo reproducirlo

```bash
docker compose stop metabase          # un .duckdb admite un solo escritor
docker compose exec lab python scripts/build_db.py
docker compose start metabase
docker compose exec lab python scripts/benchmark.py            # completo
docker compose exec lab python scripts/benchmark.py --scales 1,6,all --runs 3   # versión rápida
```

## Limitaciones a considerar al interpretar

- No se vacía la caché del sistema de archivos: la "primera ejecución" no es una medición en frío absoluto.
- Con carpetas montadas en Docker Desktop (Windows/macOS) la lectura de archivos es más lenta que en disco interno; esto afecta sobre todo a Parquet.
- En la estrategia Parquet cada consulta vuelve a leer los metadatos de todos los archivos (parte del costo real de consultar archivos directamente).
- Los tiempos dependen de CPU, memoria y de `--threads`/`--memory-limit`; registre el entorno (el script lo incluye en el `.md` generado).

## Análisis (6.9) y escenarios de uso (6.10)

<!-- COMPLETAR tras ejecutar el benchmark real:
     - Describir cómo cambia la razón Parquet/Tabla al crecer la cantidad de datos.
     - Explicar las diferencias por consulta (columnar, pruning, metadatos, compresión, costo de construcción de la tabla).
     - Discutir cuándo conviene consultar Parquet directo (datos que cambian, exploración puntual, un solo uso, sin espacio extra)
       y cuándo materializar (consultas repetidas, tablero, muchos usuarios, esquema normalizado y estable). -->
