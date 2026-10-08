# Ejercicio 9 - Discusion (preguntas 9.1 a 9.8)

> Cifras de la corrida del 2026-10-08 sobre 121,184,384 viajes (yellow y green, 2024-2026), en una maquina de 16 CPU y ~7.4 GiB de RAM para Docker. Fuentes: `docs/benchmark_results.md`, `docs/consultas_resultados.md` y `docs/benchmark_analisis.md`.

## 9.1 ¿Que caracteristicas de DuckDB resultaron mas utiles durante el laboratorio?

- **Consulta directa de Parquet con comodines** (`read_parquet('data/raw/yellow/*/*.parquet')`): permitio explorar los datos sin importar nada y sumar 2024 y 2025 sin tocar las consultas.
- **`union_by_name=true`:** absorbio columnas que aparecen o desaparecen entre archivos (`cbd_congestion_fee`, `airport_fee`).
- **Funciones de inspeccion:** `DESCRIBE`, `SUMMARIZE`, `glob()`, `parquet_schema()` y `parquet_file_metadata()` dieron esquema, perfil de calidad y conteo de archivos y filas con SQL, sin codigo adicional.
- **Funciones analiticas:** `quantile_cont`, `median`, `corr`, `count_if`, `FILTER`, funciones de ventana y `GROUP BY ALL` simplificaron el EDA.
- **Se ejecuta dentro del proceso** (como libreria de Python): sin servidor que instalar ni configurar, lo que encaja con un ambiente Docker reproducible. Un solo archivo `.duckdb` contiene la tabla materializada.
- **Rendimiento:** sobre los 121 M de filas, las agregaciones del benchmark tardaron entre 0.1 y 1.1 s con la tabla (q02 a q07) y entre 1.7 y 4.2 s directo sobre Parquet; la consulta mas pesada, la mediana y el percentil 95 (q08), tardo ~20 s en ambas estrategias.

## 9.2 ¿Que ventajas y limitaciones encontro al consultar directamente archivos Parquet?

**Ventajas**
- No hay paso de carga ni copia: un archivo nuevo entra al analisis al caer en la carpeta.
- Se lee solo lo necesario (columnas y bloques) gracias al formato columnar y a las estadisticas.
- Los datos originales no se alteran, lo que ayuda a la reproducibilidad.

**Limitaciones**
- Cada consulta vuelve a abrir y leer los metadatos de todos los archivos; con muchos archivos pequenos ese costo fijo pesa (ver benchmark: con 1 mes, Parquet fue mas rapido o igual en 7 de 8 consultas, razones de 0.23 a 0.95; con todo el conjunto la tabla fue de 3.0x a 13.7x mas rapida en q02 a q07 y 476x en el conteo).
- El esquema no esta garantizado: yellow y green usan nombres distintos y hubo columnas nuevas, asi que hace falta normalizar (`taxi_common.py`) en cada lectura.
- Los tipos podrian diferir entre archivos (`p06`); en estos datos `p06` no encontro ningun cambio de tipo, pero nada en el formato lo garantiza, por eso se mantiene `TRY_CAST`.
- No hay indices ni restricciones; la calidad de datos no se valida al leer.
- Leer archivos montados en Docker Desktop es mas lento que disco local.

## 9.3 ¿Que ventajas y limitaciones observo al utilizar tablas materializadas en DuckDB?

**Ventajas**
- Consultas repetidas mas rapidas y predecibles: con todo el conjunto, de 3.0x a 13.7x en q02 a q07 (q08, que ordena para calcular cuantiles, no mejoro: 0.95x).
- Esquema unico y tipado explicito, definido una sola vez; trazabilidad con `source_file` e `ingest_log`.
- Un solo archivo para compartir con herramientas como Metabase.

**Limitaciones**
- Costo de construccion (146.1 s) y espacio extra (3.28 GiB de `.duckdb` frente a 1.93 GiB de Parquet, 1.7 veces mas).
- Queda **desactualizada**: al llegar un mes nuevo hay que reconstruirla.
- Un archivo `.duckdb` admite un solo proceso escritor; Metabase y los notebooks deben abrirlo en solo lectura, y para reconstruir hay que detener Metabase.
- Los errores de carga se propagan a todas las consultas (por eso `build_db.py` no corrige nada y deja la limpieza para el analisis).

## 9.4 ¿Que ventajas ofrece este flujo frente a cargar todos los datos con Pandas?

- **Memoria:** Pandas carga el conjunto completo en RAM; con 121.2 millones de filas y 22 columnas de datos, a 8 bytes por valor ya serian unos 20 GiB (cuenta aproximada, no se midio), mas de los ~7.4 GiB que tuvo Docker en este laboratorio. DuckDB procesa por bloques y solo lee las columnas necesarias, y puede trabajar con datos mayores que la RAM.
- **Velocidad:** ejecucion en paralelo, columnar y vectorizada sobre archivos; Pandas ejecuta en un solo hilo en la mayoria de las operaciones.
- **Sin carga previa:** con Parquet no hay paso de lectura de todo el conjunto antes de consultar.
- **SQL declarativo:** las consultas quedan versionadas en `sql/`, son legibles para todo el equipo y se reutilizan igual en notebooks, scripts y Metabase.
- **Pandas sigue siendo util** para el ultimo paso: los notebooks traen a Pandas solo el **resultado agregado** (`.df()`) para graficarlo, no los datos crudos.

## 9.5 ¿Que caracteristicas del sistema permiten incorporar nuevos datos con cambios minimos?

- **Convencion de rutas:** `data/raw/<tipo>/<año>/<archivo>.parquet`; agregar datos es agregar archivos con ese patron.
- **Parametrizacion por año:** `download_data.py --years` reemplazo la constante `ANIO = 2026`; los años nuevos entran sin editar codigo.
- **Idempotencia:** lo que ya existe no se vuelve a descargar (archivos `.part` y validacion de tamaño), asi que se puede repetir en cualquier momento. Los meses no publicados se informan como `NO_PUBLICADO` y no como error.
- **Comodines y esquema tolerante:** las consultas leen `*/*.parquet` y `taxi_common.py` usa `union_by_name` y mapeo de nombres, por lo que absorbe columnas nuevas (`cbd_congestion_fee` desde 2025-01, `request_source` desde 2026-06) sin tocar las consultas. La evidencia esta en `docs/validacion_anios.md` (5.7 y 8.3).
- **Una sola definicion del esquema:** la tabla, la vista del benchmark, `document_queries.py` y los notebooks usan el mismo SELECT normalizado.
- **Controles automaticos:** `verify_data.py`, `v07` y `v08` detectan si falto un archivo o si la tabla no tiene las filas de los Parquet.

## 9.6 ¿Que parte del proceso deberia automatizarse en un sistema de produccion?

- **Descarga y verificacion programadas** (por ejemplo semanal, porque la TLC publica con atraso): `download_data.py` y `verify_data.py`, cuyo codigo de salida (0 o 1) puede usarse como compuerta.
- **Reconstruccion de la base:** hoy `build_db.py` reconstruye todo (146 s). En produccion convendria cargar solo los meses nuevos y reemplazar el archivo de forma atomica (ya se escribe en un `.tmp` y se renombra).
- **Refresco del tablero:** despues de reconstruir hay que reiniciar Metabase a mano porque mantiene el archivo abierto; deberia formar parte del mismo flujo. `metabase_setup.py` ya es idempotente.
- **Controles de calidad como pruebas:** ejecutar `document_queries.py` y `v07`/`v08` tras cada carga y alertar si algo falla (el script termina con codigo 1) o si el porcentaje de registros inconsistentes (`i08`) sube de forma anormal.
- **Benchmark periodico** para detectar si una consulta se degrada al crecer los datos.
- **Operacion:** credenciales en un gestor de secretos, limites de memoria (ver 9.8), respaldos del `.duckdb` y de la base de Metabase.

## 9.7 ¿Que decisiones de diseño fueron importantes para mantener el proyecto reproducible?

- **Versiones fijadas:** `requirements.txt`, imagenes de Docker con version y `duckdb` alineado con el driver de Metabase (1.5.5).
- **Datos fuera de Git y regenerables:** `.gitignore` excluye `data/raw` y `data/processed`; cualquiera los reconstruye con los scripts, sin pasarse archivos.
- **Descarga verificable:** validacion contra `Content-Length`, archivo `.part` y inventario en `docs/data_inventory.csv`.
- **Transformaciones registradas:** `build_db.py` escribe la sentencia en `sql/00_build/create_trips.sql` y no corrige datos al cargar; la limpieza queda explicita en cada consulta.
- **SQL versionado y documentado:** consultas en `sql/` con `-- Objetivo` y `-- Decision`, y `document_queries.py` que las ejecuta y genera la documentacion con resultados.
- **Benchmark comparable:** las mismas consultas y el mismo esquema en ambas estrategias, con verificacion automatica de equivalencia de resultados.
- **Tablero como codigo:** `metabase_setup.py` crea conexion, tarjetas y dashboard desde los `.sql`; las credenciales se pasan por variables de entorno y la conexion es de solo lectura.
- **Historial de Git** con commits por tema para poder rastrear cada cambio.

## 9.8 ¿Que aprendio sobre el manejo de datos que no habria sido evidente con conjuntos pequeños?

- **Los promedios engañan:** la distancia media de yellow es 5.88 millas contra una mediana de 1.81, porque hay valores imposibles (maximo 398,608 millas). Con una muestra pequeña esos casos pasan desapercibidos.
- **Los problemas raros aparecen a escala:** hay viajes con fecha de 2001 a 2009, 3.8 M de tarifas <= 0 en yellow y un 20 % de `passenger_count` nulo o 0.
- **La calidad cambia entre años:** el 9.58 % de los registros de yellow 2025 es inconsistente frente a 3.71 % en 2024 (`i08`), sobre todo por tarifas negativas.
- **El mejor formato depende del volumen:** con 1 mes de datos Parquet empata o gana; la ventaja de la tabla solo se ve al crecer (3.0x a 13.7x con todo).
- **Calcular una mediana exacta cuesta:** el indicador I6 tardo de 1 a 3 minutos con 121 M de filas. La mediana aproximada de DuckDB lo acelera, pero cambio la tarifa mediana (13.78 en vez de 13.50), asi que se mantuvo la exacta.
- **La memoria es un limite real:** un proceso de prueba fue terminado por falta de memoria (codigo 137) probablemente al competir con Metabase, que ocupaba ~2.5 GiB (la causa exacta no se aislo). Por eso la conexion de Metabase a DuckDB lleva un tope de memoria.
- **Los datos recientes estan incompletos:** 2026 llega hasta agosto, asi que se compara el mismo mes entre años y no años completos.
- **Verificar lo que se afirma:** al contrastar las conclusiones con una consulta aparecio un error propio (el dia de menor demanda es el lunes, no el domingo), lo que muestra la utilidad de documentar cada resultado con su consulta.
