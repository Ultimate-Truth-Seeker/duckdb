# Lab 8 - DuckDB

Repositorio base del laboratorio 8 del curso **CC3084 - Data Science**
(Universidad del Valle de Guatemala, Ciclo 2, 2026).

Este es el repositorio **proporcionado por el docente**. Contiene la estructura
del proyecto, el ambiente de ejecucion basado en Docker y un script que descarga
los datos de **2026**. Todo lo demas debe ser construido por cada equipo.

## Trabajo con fork

El laboratorio se desarrolla y se entrega sobre un **fork** de este repositorio.
No se trabaja directamente sobre el repositorio del docente.

1. Realice un fork de este repositorio:
   <https://github.com/menene/duckdb>

2. Clone **su propio fork** (no el del docente):

   ```bash
   git clone https://github.com/<su-usuario>/duckdb.git
   cd duckdb
   ```

3. Opcional, para recibir correcciones publicadas por el docente:

   ```bash
   git remote add upstream https://github.com/menene/duckdb.git
   git fetch upstream
   ```

Realice commits frecuentes y descriptivos: el historial del repositorio es parte
de la evaluacion. **La entrega del laboratorio es la URL de su fork.**

## Estructura

```text
duckdb/
|
+-- data/
|   +-- raw/
|   +-- processed/
|
+-- notebooks/
|
+-- scripts/
|
+-- sql/
|
+-- docs/
|
+-- Dockerfile
+-- metabase.Dockerfile
+-- docker-compose.yml
+-- README.md
```

## Requisitos

- Docker, con Docker Compose
- Git

La primera construccion del ambiente descarga varios cientos de MB y puede
tardar algunos minutos.

Considere el espacio en disco: las imagenes de Docker ocupan unos 3 GB y los
datos de los tres anios del laboratorio superan 1.5 GB, a los que se suma la
base materializada del Ejercicio 6. Se recomienda tener al menos 10 GB libres.

## Datos

El repositorio incluye `scripts/download_data.py`, que descarga los archivos de
2026 publicados por la TLC (`--help` muestra las opciones disponibles). Los
archivos se guardan en `data/raw/<tipo>/<anio>/`.

La TLC publica cada mes con varias semanas de atraso, por lo que los ultimos
meses de 2026 todavia no existen. El script consulta al servidor que meses estan
publicados, de modo que vuelve a ejecutarse sin problema conforme aparezcan
nuevos archivos.

Los datos descargados **no deben incluirse en el repositorio Git**. El archivo
`.gitignore` ya esta configurado para evitarlo.

Fuente de datos: NYC TLC Trip Record Data
<https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page>

Dentro de los contenedores, la carpeta `data/` del proyecto esta montada en
`/workspace/data`. Esa es la ruta que deben usar las herramientas que corren
dentro del ambiente, no la ruta de su computadora.

> **Nota sobre DuckDB:** un archivo `.duckdb` admite un solo proceso con permiso
> de escritura a la vez. Si conecta una herramienta externa a su base de datos,
> use el modo de solo lectura (`read_only`) en esa conexion; de lo contrario los
> demas procesos no podran abrir el archivo.

## Material a entregar

Al finalizar, su fork debe contener:

- el codigo fuente modificado y los scripts de descarga;
- las consultas SQL desarrolladas;
- el notebook o notebooks utilizados;
- la documentacion de las consultas;
- los scripts utilizados para los benchmarks;
- el codigo de los indicadores y visualizaciones;
- el tablero o la evidencia del tablero desarrollado;
- este `README.md`, completado segun la siguiente seccion.

Los archivos de datos descargados **no** deben incluirse.

---

# Documentacion del equipo

Las siguientes secciones deben ser completadas por cada equipo. El README final
debe permitir que una persona que no participo en el desarrollo pueda levantar el
ambiente, descargar los datos, ejecutar el analisis, reproducir los benchmarks y
generar los resultados principales.

## Como levantar el ambiente

### Requisitos previos
Docker con Docker Compose, Git y ~10 GB de disco libre.

### Pasos
```bash
# 1. Fork del repositorio del docente (desde GitHub) y clonado de SU fork
git clone https://github.com/<su-usuario>/duckdb.git
cd duckdb

# 2. Construir y levantar los servicios (la primera vez tarda varios minutos)
docker compose up --build -d

# 3. Verificar
docker compose ps
docker compose exec lab python -c "import duckdb; print(duckdb.__version__)"
```

| Servicio | URL | Notas |
|---|---|---|
| JupyterLab (`lab`) | <http://localhost:8888> | Sin token; solo accesible desde `127.0.0.1`. |
| Metabase (`metabase`) | <http://localhost:3000> | La primera vez pide crear una cuenta local. |

**Conectar Metabase a DuckDB:** Admin > Databases > Add database > DuckDB, archivo
`/workspace/data/processed/taxi.duckdb` (existe despues de ejecutar `scripts/build_db.py`).
Active el modo **solo lectura** de la conexion (ver la nota sobre `read_only` mas arriba).

Para detener: `docker compose down` (conserva los datos y la configuracion de Metabase).

Todos los comandos de Python de este README se ejecutan **dentro del contenedor**:
`docker compose exec lab <comando>`. Mas detalles (estructura de directorios, herramientas del
ambiente, importancia de la reproducibilidad) en [`docs/ambiente.md`](docs/ambiente.md).

## Como descargar los datos

```bash
# Descarga yellow y green de 2024, 2025 y 2026 en data/raw/<tipo>/<anio>/
docker compose exec lab python scripts/download_data.py

# Opciones
docker compose exec lab python scripts/download_data.py --years 2026        # solo algunos anios
docker compose exec lab python scripts/download_data.py --taxi green
docker compose exec lab python scripts/download_data.py --dry-run           # sin descargar

# Verificar que el conjunto esta completo e integro (escribe docs/data_inventory.csv)
docker compose exec lab python scripts/verify_data.py
```
- Los archivos ya descargados **no** se vuelven a descargar: el comando puede repetirse cuando la TLC
  publique meses nuevos.
- Los meses que la TLC aun no publica se reportan como `NO_PUBLICADO` (no es un error).
- Si `verify_data.py` reporta `FALTA` o `INVALIDO`, ejecute `verify_data.py --delete-invalid` y luego
  `download_data.py` de nuevo.

Cambios realizados al script original y como se verifica la completitud: [`docs/descarga.md`](docs/descarga.md).

## Como ejecutar el analisis

<!-- TODO -->

## Como reproducir los benchmarks

```bash
# 1. Materializar la tabla (detenga Metabase: un .duckdb admite un solo escritor)
docker compose stop metabase
docker compose exec lab python scripts/build_db.py        # crea data/processed/taxi.duckdb
docker compose start metabase

# 2. Ejecutar el benchmark (consultas en sql/04_benchmark/)
docker compose exec lab python scripts/benchmark.py
docker compose exec lab python scripts/benchmark.py --scales 1,6,all --runs 3   # version rapida
```
Resultados: `docs/benchmark_results.csv` y `docs/benchmark_results.md`.
Metodologia, consultas y limitaciones: [`docs/benchmark.md`](docs/benchmark.md).

## Como generar los resultados principales

<!-- TODO -->
