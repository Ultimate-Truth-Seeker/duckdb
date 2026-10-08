# Ejercicio 9 - Discusion (preguntas 9.1 a 9.4)

> **Borrador.** Las respuestas se apoyan en lo que se hizo en el proyecto; las partes entre `[ ]` deben reemplazarse con las cifras reales del equipo (conteos de `p02`, tiempos de `docs/benchmark_results.md`) antes de entregar.

## 9.1 ¿Que caracteristicas de DuckDB resultaron mas utiles durante el laboratorio?

- **Consulta directa de Parquet con comodines** (`read_parquet('data/raw/yellow/*/*.parquet')`): permitio explorar los datos sin importar nada y sumar 2024 y 2025 sin tocar las consultas.
- **`union_by_name=true`:** absorbio columnas que aparecen o desaparecen entre archivos (`cbd_congestion_fee`, `airport_fee`).
- **Funciones de inspeccion:** `DESCRIBE`, `SUMMARIZE`, `glob()`, `parquet_schema()` y `parquet_file_metadata()` dieron esquema, perfil de calidad y conteo de archivos y filas con SQL, sin codigo adicional.
- **Funciones analiticas:** `quantile_cont`, `median`, `corr`, `count_if`, `FILTER`, funciones de ventana y `GROUP BY ALL` simplificaron el EDA.
- **Se ejecuta dentro del proceso** (como libreria de Python): sin servidor que instalar ni configurar, lo que encaja con un ambiente Docker reproducible. Un solo archivo `.duckdb` contiene la tabla materializada.
- **Rendimiento:** [citar el tiempo de la consulta mas pesada sobre los tres anios].

## 9.2 ¿Que ventajas y limitaciones encontro al consultar directamente archivos Parquet?

**Ventajas**
- No hay paso de carga ni copia: un archivo nuevo entra al analisis al caer en la carpeta.
- Se lee solo lo necesario (columnas y bloques) gracias al formato columnar y a las estadisticas.
- Los datos originales no se alteran, lo que ayuda a la reproducibilidad.

**Limitaciones**
- Cada consulta vuelve a abrir y leer los metadatos de todos los archivos; con muchos archivos pequenos ese costo fijo pesa (ver benchmark: [razon Parquet/Tabla con 1 mes frente a todo el conjunto]).
- El esquema no esta garantizado: yellow y green usan nombres distintos y hubo columnas nuevas, asi que hace falta normalizar (`taxi_common.py`) en cada lectura.
- Los tipos pueden diferir entre archivos (`p06`); sin `TRY_CAST` una consulta puede fallar a medias.
- No hay indices ni restricciones; la calidad de datos no se valida al leer.
- Leer archivos montados en Docker Desktop es mas lento que disco local.

## 9.3 ¿Que ventajas y limitaciones observo al utilizar tablas materializadas en DuckDB?

**Ventajas**
- Consultas repetidas mas rapidas y predecibles: [razon Parquet/Tabla en las consultas q02 a q08].
- Esquema unico y tipado explicito, definido una sola vez; trazabilidad con `source_file` e `ingest_log`.
- Un solo archivo para compartir con herramientas como Metabase.

**Limitaciones**
- Costo de construccion ([build_seconds] s) y espacio extra ([db_gb] GiB frente a [gb_parquet] GiB de Parquet).
- Queda **desactualizada**: al llegar un mes nuevo hay que reconstruirla.
- Un archivo `.duckdb` admite un solo proceso escritor; Metabase y los notebooks deben abrirlo en solo lectura, y para reconstruir hay que detener Metabase.
- Los errores de carga se propagan a todas las consultas (por eso `build_db.py` no corrige nada y deja la limpieza para el analisis).

## 9.4 ¿Que ventajas ofrece este flujo frente a cargar todos los datos con Pandas?

- **Memoria:** Pandas carga el conjunto completo en RAM; con [N millones de filas segun p02] y varias columnas de texto y fecha, un laptop se queda sin memoria. DuckDB procesa por bloques y solo lee las columnas necesarias, y puede trabajar con datos mayores que la RAM.
- **Velocidad:** ejecucion en paralelo, columnar y vectorizada sobre archivos; Pandas ejecuta en un solo hilo en la mayoria de las operaciones.
- **Sin carga previa:** con Parquet no hay paso de lectura de todo el conjunto antes de consultar.
- **SQL declarativo:** las consultas quedan versionadas en `sql/`, son legibles para todo el equipo y se reutilizan igual en notebooks, scripts y Metabase.
- **Pandas sigue siendo util** para el ultimo paso: los notebooks traen a Pandas solo el **resultado agregado** (`.df()`) para graficarlo, no los datos crudos.
