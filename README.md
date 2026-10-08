# Lab 8 - DuckDB

Laboratorio 8 del curso **CC3084 - Data Science** (Universidad del Valle de Guatemala, Ciclo 2, 2026).
Análisis de los viajes de taxi de NYC (TLC Trip Record Data, yellow y green, 2024-2026) con DuckDB:
consulta directa de Parquet, tabla materializada, benchmark e indicadores en Metabase.

Fuente de datos: <https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page>

## Estructura

```text
data/raw/         Parquet originales de la TLC (<tipo>/<año>/*.parquet). No se versiona.
data/processed/   Base materializada taxi.duckdb. No se versiona.
notebooks/        01_exploracion, 02_eda, 03_validacion_y_benchmark
scripts/          descarga, verificación, construcción de la base, benchmark, documentación de consultas
sql/              consultas versionadas: 00_build (generada), 01_exploracion, 02_eda, 03_validacion_anios, 04_benchmark, 05_indicadores
docs/             documentación, resultados del benchmark e inventario de datos
```

Detalle del propósito de cada carpeta: `docs/ambiente.md`.

## Requisitos

- Docker con Docker Compose y Git.
- Unos 10 GB libres: imágenes de Docker (~3 GB), Parquet (~2 GB) y base materializada (~3.3 GB).
- Docker Desktop con al menos 8 GB de RAM (el benchmark se midió con ~7.9 GB).

## Cómo levantar el ambiente

```bash
git clone <url-del-fork> && cd duckdb
docker compose up --build -d
docker compose ps
docker compose exec lab python -c "import duckdb; print(duckdb.__version__)"   # 1.5.5
```

- JupyterLab: <http://localhost:8888> (sin token, solo escucha en `127.0.0.1`).
- Metabase: <http://localhost:3000> (la primera vez pide crear una cuenta local).
- Dentro de los contenedores, `data/` está montada en `/workspace/data`.

La versión de `duckdb` en `requirements.txt` debe mantenerse igual a la del driver de DuckDB de
`metabase.Dockerfile`, porque Metabase abre el mismo `.duckdb`.

> Un `.duckdb` admite **un solo proceso con permiso de escritura**. Para reconstruir la base hay que
> detener Metabase (`docker compose stop metabase`) y cerrar notebooks que la tengan abierta.
> Cualquier otra herramienta debe abrirla en modo solo lectura (`read_only`).

## Cómo descargar los datos

Todos los comandos corren dentro del contenedor `lab`:

```bash
docker compose exec lab python scripts/download_data.py --dry-run     # solo informa
docker compose exec lab python scripts/download_data.py               # yellow+green 2024-2026
docker compose exec lab python scripts/download_data.py --years 2026  # solo algunos años
docker compose exec lab python scripts/verify_data.py                 # verifica y escribe docs/data_inventory.csv
```

- Los archivos se guardan en `data/raw/<tipo>/<año>/` y **no se vuelven a descargar** si ya existen.
- La TLC publica con atraso: los últimos meses de 2026 aparecen como `NO_PUBLICADO` y no es un error.
- `verify_data.py` termina con código 0 solo si todo lo publicado está presente, con el tamaño correcto y legible.
- Resultado de referencia (2026-10-08): 64 archivos OK, 121,184,384 filas. Cambios al script y criterio de completitud: `docs/descarga.md`.

## Cómo ejecutar el análisis

1. Construir la base materializada (~2.5 min con los 3 años; Metabase detenido):

   ```bash
   docker compose stop metabase
   docker compose exec lab python scripts/build_db.py
   docker compose start metabase
   ```

   Genera `data/processed/taxi.duckdb` (tablas `trips`, `ingest_log`, `build_info`) y registra la
   transformación en `sql/00_build/create_trips.sql`. No se filtra ni corrige ningún dato al cargar.

2. Ejecutar y documentar todas las consultas de `sql/` (genera `docs/consultas_resultados.md`):

   ```bash
   docker compose exec lab python scripts/document_queries.py                  # lee los Parquet
   docker compose exec lab python scripts/document_queries.py --source tabla   # usa la tabla
   ```

   Termina con código 1 si alguna consulta falla. La decisión de cada consulta está en su `.sql` (`-- Decision:`).

3. Abrir los notebooks de `notebooks/` en JupyterLab. Las salidas guardadas se generaron así: el `01` leyendo los
   Parquet directamente (Ej. 3) y el `02` y el `03` sobre la tabla (`LAB_FUENTE=tabla`). Por defecto leen los Parquet; con `LAB_FUENTE=tabla`
   (variable de entorno al iniciar Jupyter) leen la tabla en solo lectura.

La documentación de cada ejercicio está en `docs/`: `exploracion.md` (Ej. 3), `eda.md` (Ej. 4),
`validacion_anios.md` (Ej. 5 y 8.3), `benchmark.md` y `benchmark_analisis.md` (Ej. 6), `discusion_B.md` (Ej. 9).

## Cómo reproducir los benchmarks

Con la base ya construida y Metabase detenido (un solo escritor):

```bash
docker compose stop metabase
docker compose exec lab python scripts/benchmark.py                           # completo: escalas 1,3,6,12,24 y todo, 5 corridas
docker compose exec lab python scripts/benchmark.py --scales 1,6,all --runs 3 # versión rápida
docker compose start metabase
```

Compara las mismas consultas (`sql/04_benchmark/q*.sql`) sobre Parquet directo y sobre la tabla, y
comprueba que los resultados sean equivalentes. Salida: `docs/benchmark_results.csv` y `docs/benchmark_results.md`.
Los tiempos dependen de la máquina; el entorno queda registrado en el `.md` generado.

## Cómo generar los resultados principales

| Resultado | Comando / archivo |
|---|---|
| Inventario de datos | `scripts/verify_data.py` -> `docs/data_inventory.csv` |
| Resultado de cada consulta | `scripts/document_queries.py` -> `docs/consultas_resultados.md` |
| Benchmark | `scripts/benchmark.py` -> `docs/benchmark_results.{csv,md}` |
| Gráficas del análisis | notebooks `01`, `02` y `03` |
| Tablero e indicadores | `sql/05_indicadores/` + `scripts/metabase_setup.py` (sección siguiente) |

## Cómo generar el tablero (Ejercicio 7)

Los 8 indicadores están en `sql/05_indicadores/i01..i08.sql` (cada uno con su pregunta, justificación y decisión).
`scripts/metabase_setup.py` los carga en Metabase por su API: crea la cuenta local de administrador, conecta
`taxi.duckdb` en **solo lectura** con tope de memoria, crea una tarjeta por indicador y arma el dashboard
"Lab 8 - Taxis NYC". Es idempotente: se puede repetir sin duplicar nada.

Requiere la base ya construida y Metabase levantado. Las credenciales se pasan por variables de entorno y
**no se guardan en el repositorio** (elija una contraseña propia):

```bash
export MB_ADMIN_EMAIL=admin@lab8.local
export MB_ADMIN_PASSWORD='<contraseña-local>'
docker compose exec -e MB_ADMIN_EMAIL -e MB_ADMIN_PASSWORD lab python scripts/metabase_setup.py
```

Luego abrir <http://localhost:3000> e iniciar sesión con esa cuenta; el dashboard está en la colección "Lab 8 - Taxis NYC".

- La tarjeta I6 (medianas exactas sobre 121 M de filas) es la más lenta: puede tardar de 2 a 3 minutos en cargar.
- Si reconstruye la base (`build_db.py`), reinicie Metabase después (`docker compose restart metabase`).
- Si el script avisa que no pudo actualizar la conexión, reinicie Metabase y vuelva a ejecutarlo.
- Evidencia del tablero: `docs/tablero/`.

## Datos

Los archivos de datos **no se incluyen en Git** (`.gitignore` cubre `data/raw/**` y `data/processed/**`).
Cualquier persona los regenera con los scripts de arriba; no hace falta pasarlos a mano.
