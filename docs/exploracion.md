# Ejercicio 3 - Consultas directas sobre archivos Parquet

Consultas: `sql/01_exploracion/p01..p12`. Notebook: `notebooks/01_exploracion.ipynb`.
Resultado, fuente y decision de cada consulta: `docs/consultas_resultados.md` (se genera con `python scripts/document_queries.py --dirs 01_exploracion`).

## Que punto responde cada consulta

| Punto | Consulta |
|---|---|
| 3.1 archivos | `p01_archivos.sql` |
| 3.2 registros | `p02_registros.sql` |
| 3.3 columnas | `p03`, `p04`, `p05`, `p07` |
| 3.4 tipos de datos | `p03`, `p04`, `p05`, `p06` |
| 3.5 muestra | `p08_muestra.sql` |
| 3.6 calidad | `p06`, `p07`, `p09`, `p10`, `p11`, `p12` |
| 3.7 consulta directa | todas leen `read_parquet(...)`, `glob(...)` o `parquet_schema(...)`; ninguna usa una tabla |
| 3.8 documentacion | `docs/consultas_resultados.md` (SQL, objetivo, fuente, resultado, decision) |

Los patrones usan comodin de anio (`data/raw/yellow/*/*.parquet`), de modo que al descargar 2024 y 2025 **no cambia ninguna consulta** (ver `docs/validacion_anios.md`).

## 3.6 Problemas de calidad de datos

Esta lista dice **que buscar y con que consulta**. Los hallazgos con cifras salen de ejecutar `p09` a `p12` sobre los datos reales y deben anotarse en la columna "Resultado" antes de entregar.

| Posible problema | Se detecta con | Decision prevista |
|---|---|---|
| Fechas de recogida fuera del anio/mes del archivo | `p11`, `p12`, `v03` | Excluir del analisis temporal; no se borran de `trips`. |
| Bajada anterior a la recogida, o duracion > 24 h | `p11`, `d02` | Excluir de duracion y velocidad. |
| Distancia 0 o muy grande (> 100 millas) | `p09`, `p10`, `p11` | Filtrar en indicadores de distancia y velocidad. |
| Tarifa o total negativos o en cero (devoluciones, disputas, viajes anulados) | `p09`, `p11` | Filtrar `fare_amount` entre 1 y 500 en promedios. |
| `passenger_count` nulo o 0 | `p09`, `p10`, `p11` | No usar como filtro; reportar el % de nulos. |
| Zonas de recogida fuera de 1-265 | `p11` | Excluir de los analisis por zona. |
| Columnas que existen solo en un tipo o desde cierto anio (`cbd_congestion_fee`, `airport_fee`, `ehail_fee`, `trip_type`) | `p05`, `p07` | Tratarlas como NULL donde no existen (`taxi_common.py`). |
| Mismo campo con tipo distinto entre archivos o con distinto nombre (`Airport_fee`/`airport_fee`, `tpep_*`/`lpep_*`) | `p06`, `p05` | `union_by_name=true`, `TRY_CAST` y mapeo de nombres. |

## 3.9 ¿Que significa consultar directamente un archivo Parquet y por que sirve con volumenes grandes?

Consultar directamente un Parquet es escribir `SELECT ... FROM read_parquet('ruta/*.parquet')` y que DuckDB lea los archivos **en el momento de la consulta**, sin crear una tabla ni copiar los datos antes. Los archivos siguen siendo la unica copia de los datos.

Es util con mucho volumen por cuatro razones:

1. **Formato columnar:** Parquet guarda cada columna por separado; una consulta que usa 3 de 20 columnas lee solo esas 3.
2. **Estadisticas por bloque:** cada archivo guarda minimo y maximo por grupo de filas, y un filtro como `fare_amount > 500` puede saltarse bloques completos. Un `count(*)` puede resolverse casi solo con los metadatos.
3. **Sin carga previa:** no hay que esperar una importacion ni reservar espacio extra; un archivo nuevo en la carpeta ya forma parte de la consulta.
4. **No exige memoria para todo el conjunto:** DuckDB procesa por bloques y en paralelo, y puede ejecutar consultas sobre mas datos que RAM.

El costo es que cada consulta vuelve a abrir los archivos, leer sus metadatos y, si hay que unificar esquemas, convertir tipos; eso se mide en el benchmark del Ejercicio 6 (`docs/benchmark_analisis.md`).
