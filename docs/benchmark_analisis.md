# Análisis del benchmark (6.9 y 6.10)

Datos: `docs/benchmark_results.csv` y `benchmark_results.md` (generados por `scripts/benchmark.py`; metodología en [`benchmark.md`](benchmark.md)).
Entorno de la corrida: DuckDB 1.5.5, 16 CPU, hilos y memoria por defecto, 5 ejecuciones por consulta (se usa la mediana), Docker Desktop en Windows con la carpeta `data/` montada.
Todas las comparaciones devolvieron resultados equivalentes (96 filas del CSV con `resultado_equivalente = True`).

## 6.9 Cómo cambia el rendimiento con la cantidad de datos

Razón **Parquet / Tabla** de la mediana (mayor que 1: la tabla fue más rápida; menor que 1: ganó Parquet).

| Meses | Filas (M) | GiB Parquet | q01 | q02 | q03 | q04 | q05 | q06 | q07 | q08 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 3.0 | 0.05 | 0.23 | 0.95 | 0.72 | 0.41 | 0.94 | 0.63 | 0.58 | 1.06 |
| 3 | 9.7 | 0.15 | 0.57 | 1.37 | 1.08 | 0.93 | 1.70 | 0.96 | 1.00 | 0.93 |
| 6 | 20.7 | 0.33 | 0.87 | 1.77 | 1.73 | 1.47 | 3.04 | 1.73 | 1.78 | 0.85 |
| 12 | 41.8 | 0.66 | 1.51 | 2.23 | 2.65 | 2.78 | 4.05 | 2.57 | 2.22 | 1.17 |
| 24 | 91.1 | 1.45 | 3.42 | 2.53 | 3.28 | 3.67 | 4.49 | 3.34 | 3.47 | 1.09 |
| 32 (todo) | 121.2 | 1.93 | 476.50 | 2.99 | 4.98 | 13.66 | 7.64 | 5.81 | 5.62 | 0.95 |

Tiempos con todos los datos (121 M de filas), en segundos:

| Consulta | Parquet | Tabla | Razón |
|---|---:|---:|---:|
| q01 conteo total | 0.762 | 0.002 | 476.50 |
| q02 viajes por mes y tipo | 3.151 | 1.052 | 2.99 |
| q03 tarifas por tipo de pago | 2.758 | 0.554 | 4.98 |
| q04 top zonas | 1.681 | 0.123 | 13.66 |
| q05 perfil día y hora | 3.447 | 0.451 | 7.64 |
| q06 filtro selectivo | 2.634 | 0.454 | 5.81 |
| q07 varias columnas | 4.206 | 0.748 | 5.62 |
| q08 mediana y percentil | 19.357 | 20.298 | 0.95 |

### Lo que se observa

- **Con poco dato, Parquet gana o empata.** Con 1 mes (3 M de filas, 2 archivos) Parquet fue más rápido o igual en 7 de 8 consultas (razones de 0.23 a 0.95); solo q08 dio 1.06.
- **La ventaja de la tabla crece con el volumen.** Desde 6 meses la tabla gana en q02 a q07 (1.5x a 3.0x) y con 24 meses la razón está entre 2.5x y 4.5x.
- **Tiempos vs filas.** De 1 mes a todo, las filas se multiplican por 40. El tiempo de Parquet se multiplica por 13 a 17 en las consultas de agregación (q02 a q07) y el de la tabla por 0.5 a 4. En q08 ambas estrategias crecen 23x y 26x, es decir, de forma cercana a lineal.
- **q01 (conteo):** la tabla responde en 1.6 ms usando metadatos; con Parquet hay que abrir los 64 archivos (0.76 s). La razón de 476x solo ocurre con el conjunto completo.
- **q08 (mediana y percentil 95):** casi sin diferencia (0.85x a 1.17x). Ambas estrategias tardan ~20 s con todo el conjunto: el costo es calcular cuantiles, no leer.
- **Primera ejecución:** en Parquet con todo el conjunto, q02 y q03 tardaron 4.3 s y 4.0 s la primera vez frente a 3.2 s y 2.8 s de mediana (efecto de caché). En las demás consultas la primera ejecución fue similar a la mediana.

### Explicaciones probables (no medidas por separado)

- La tabla guarda las columnas ya tipadas y normalizadas en un solo archivo; la vista sobre Parquet repite en cada consulta el renombrado y `TRY_CAST` y lee el pie de los 64 archivos. Ese costo fijo pesa más cuando se consulta poco dato.
- En q04 la razón sube de 3.67 (24 meses) a 13.66 (todo). Puede deberse en parte a la limitación descrita abajo (filtro adicional en escalas parciales).
- Es una hipótesis que no se aisló: esta corrida no midió por separado el costo de normalizar ni el de leer metadatos.

## Costo de materializar

- Construcción de la tabla: 146.1 s para 121,184,384 filas.
- Tamaño: el `.duckdb` ocupa **3.28 GiB** contra **1.93 GiB** de Parquet (1.7x más). La tabla no ahorra espacio, lo duplica.
- Ejecuciones de equilibrio con todo el conjunto, `146.1 s / (tiempo Parquet - tiempo Tabla)`:

| Consulta | Ejecuciones para recuperar la construcción |
|---|---:|
| q07 | 42 |
| q05 | 49 |
| q03 | 66 |
| q06 | 67 |
| q02 | 70 |
| q04 | 94 |
| q01 | 192 |
| q08 | nunca (la tabla no fue más rápida) |

Es decir, la construcción se paga con unas decenas de ejecuciones de consultas de agregación, que es lo normal en un tablero con varios usuarios.

## 6.10 Cuándo conviene cada estrategia

| Situación | Estrategia | Razón (respaldo) |
|---|---|---|
| Exploración puntual o un solo uso | Parquet directo | No hay construcción ni 3.28 GiB extra; con pocos datos Parquet empata o gana (escala de 1 mes). |
| Datos que llegan seguido (meses nuevos) | Parquet directo, o reconstruir la tabla de forma programada | Un archivo nuevo entra solo a la consulta; la tabla queda desactualizada hasta reconstruirse (146 s). |
| Consultas repetidas, tablero (Metabase), varios usuarios | Tabla materializada | 3x a 14x más rápida en agregaciones con todo el conjunto; el costo se recupera en ~42 a 94 ejecuciones. |
| Esquema normalizado y estable que otros consumen | Tabla materializada | Un solo esquema tipado, con trazabilidad (`source_file`, `ingest_log`) y un solo archivo que abre Metabase. |
| Poco espacio en disco | Parquet directo | La tabla ocupa 1.7x lo que ocupan los Parquet. |
| Cálculos dominados por ordenar (cuantiles) | Cualquiera | q08 no mejora con la tabla (0.95x). |

**Recomendación para este proyecto:** explorar con Parquet directo y usar la tabla materializada como fuente del tablero. Con 3 años (121 M de filas) las consultas de agregación (q02 a q07) bajan de 1.7-4.2 s a 0.1-1.1 s, y la base se reconstruye en ~2.5 minutos cuando la TLC publique meses nuevos.

## Limitaciones

- Un solo equipo y entorno: los tiempos dependen de CPU, memoria, Docker y de que `data/` esté montada (más lenta que disco interno en Windows y macOS).
- No se vacía la caché del sistema operativo entre ejecuciones.
- **En escalas parciales la tabla tiene un costo extra:** `benchmark.py` crea la vista con `WHERE source_file IN (...)`, mientras que con todo el conjunto usa `SELECT * FROM tdb.trips` sin filtro. Por eso la ventaja de la tabla en escalas parciales está algo subestimada y el salto de 24 meses a todo (por ejemplo q04, de 3.67x a 13.66x) mezcla el efecto del volumen con el de ese filtro.
- Las escalas toman los primeros N meses cronológicos, y los meses no tienen el mismo tamaño.
- Una sola corrida de 5 repeticiones por consulta y escala; no se calculó dispersión.
