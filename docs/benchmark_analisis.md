# Analisis del benchmark (6.9 y 6.10)

Datos de entrada: `docs/benchmark_results.csv` (generado por `scripts/benchmark.py`; ver metodologia en [`benchmark.md`](benchmark.md)).
Graficas y tablas de razon: `notebooks/03_validacion_y_benchmark.ipynb`, parte 2.

> Las secciones marcadas con **[DATOS]** deben completarse con las cifras reales del benchmark del equipo. El resto es el marco de interpretacion.

## 6.9 Como cambia el rendimiento con la cantidad de datos

**[DATOS]** Tabla con la razon Parquet/Tabla (mediana) por escala (1, 3, 6, 12, 24 meses y todo) y su grafica. Responder:

- A partir de que escala la ventaja de la tabla se hace visible y si la razon crece, se estabiliza o baja.
- Si el tiempo de cada estrategia crece de forma aproximadamente lineal con las filas.
- Si hay escalas donde Parquet gana o empata (esperable con 1 mes, donde el costo fijo domina).

### Diferencias por consulta

| Consulta | Que se espera | Por que |
|---|---|---|
| `q01_conteo_total` | Parquet muy competitivo | El conteo se puede resolver con los metadatos de los archivos, sin leer columnas. |
| `q02`, `q03`, `q05` (agregaciones) | Tabla mas rapida | Leen pocas columnas; la tabla evita abrir cada archivo, leer su footer y convertir tipos con `TRY_CAST` en cada ejecucion. |
| `q04` (Top-N) | Tabla mas rapida | `GROUP BY` sobre una columna entera; el costo restante es de lectura. |
| `q06` (filtro selectivo) | Ventaja menor para la tabla | Ambos formatos guardan estadisticas min/max por bloque y descartan bloques; la vista sobre Parquet ademas aplica `TRY_CAST`, lo que puede limitar el descarte. |
| `q07` (muchas columnas) | Brecha menor | Se leen casi todas las columnas numericas: se pierde la ventaja de leer solo lo necesario. |
| `q08` (mediana, percentil) | Tiempos altos en ambos | Requiere ordenar/agrupar valores; domina el calculo, no la lectura. |

**[DATOS]** Contrastar esta tabla de expectativas con los resultados reales y explicar cualquier sorpresa.

### Factores que explican las diferencias

- **Almacenamiento columnar y proyeccion:** solo se leen las columnas usadas por la consulta, en ambas estrategias.
- **Costo de metadatos:** con Parquet directo se abren y leen los metadatos de todos los archivos en cada consulta; la tabla ya los tiene en un solo archivo.
- **Normalizacion:** la vista sobre Parquet repite el renombrado y `TRY_CAST` por cada ejecucion; la tabla lo pago una sola vez al construirse.
- **Compresion y codificacion:** el `.duckdb` y los Parquet comprimen distinto; comparar el tamano en disco (`gb_parquet` frente a `db_gb`).
- **Cache:** la primera ejecucion (entre parentesis en `benchmark_results.md`) no es una medicion en frio absoluto; usar la mediana para comparar.

## Costo de materializar

**[DATOS]** Tiempo de construccion (`build_seconds`) y tamano del `.duckdb` frente a los Parquet. Estimar en cuantas ejecuciones de una consulta tipica se recupera el costo de construir la tabla:

`ejecuciones de equilibrio = tiempo de construccion / (tiempo Parquet - tiempo Tabla)`

## 6.10 Cuando conviene cada estrategia

| Situacion | Estrategia recomendada | Razon |
|---|---|---|
| Exploracion puntual o de un solo uso | Parquet directo | No hay costo de construccion ni espacio adicional. |
| Datos que cambian o llegan seguido (nuevos meses) | Parquet directo, o reconstruir la tabla de forma programada | La tabla queda desactualizada hasta reconstruirse. |
| Consultas repetidas, tablero (Metabase), muchos usuarios | Tabla materializada | El costo de construir se amortiza y las consultas son mas rapidas y predecibles. |
| Esquema normalizado y estable que otros consumen | Tabla materializada | Un solo esquema documentado, con trazabilidad (`source_file`, `ingest_log`). |
| Poco espacio en disco | Parquet directo | La tabla duplica los datos en otro formato. |

**[DATOS]** Cerrar con la recomendacion del equipo para este proyecto, respaldada por las cifras (volumen de 3 anios, frecuencia de las consultas del tablero).

## Limitaciones

- Un solo equipo y un solo entorno: los tiempos dependen de CPU, memoria y de Docker (carpetas montadas mas lentas en Windows/macOS).
- No se vacia la cache del sistema operativo entre ejecuciones.
- Las escalas toman los primeros N meses cronologicos; los meses no tienen el mismo tamano.
