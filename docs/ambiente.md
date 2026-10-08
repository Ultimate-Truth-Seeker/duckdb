# Ambiente de trabajo (Ejercicio 1)

## Propósito de cada directorio (análisis de la estructura)

| Directorio | Propósito |
|---|---|
| `data/raw/` | Datos **originales e inmutables** tal como los publica la TLC (`<tipo>/<año>/*.parquet`). Nunca se editan a mano; se pueden regenerar con el script de descarga. |
| `data/processed/` | Datos **derivados**: la base `taxi.duckdb` materializada y cualquier salida intermedia. Se pueden reconstruir a partir de `raw/` con `scripts/build_db.py`. |
| `notebooks/` | Exploración y análisis interactivo (Jupyter) con las explicaciones e interpretaciones. |
| `scripts/` | Código **reproducible y ejecutable desde la línea de comandos**: descarga, verificación, construcción de la base y benchmarks. |
| `sql/` | Consultas SQL versionadas, separadas del código Python para poder revisarlas y reutilizarlas (exploración, EDA, benchmark, indicadores). |
| `docs/` | Documentación: consultas, decisiones, resultados de benchmarks, evidencia del tablero, discusión. |
| `Dockerfile`, `metabase.Dockerfile`, `docker-compose.yml` | Definen el ambiente de ejecución (Python/Jupyter y Metabase). |
| `README.md` | Punto de entrada: cómo levantar, descargar, ejecutar y reproducir. |

Los datos (`data/`) están montados dentro de los contenedores en `/workspace/data` y **no se versionan en Git**.

## 1.3 Verificación de los servicios

```bash
docker compose up --build -d
docker compose ps                                   # lab8-lab y lab8-metabase en estado "running"
docker compose exec lab python -c "import duckdb; print(duckdb.__version__)"
docker compose logs --tail 20 metabase              # debe terminar indicando que Metabase está inicializado
```
- JupyterLab: <http://localhost:8888> (sin token; solo escucha en `127.0.0.1`).
- Metabase: <http://localhost:3000> (la primera vez pide crear una cuenta local).

## 1.4 Herramientas disponibles

Según los Dockerfiles del repositorio:

**Contenedor `lab`** (`python:3.11.14-slim`): Python 3.11, JupyterLab, `curl` y certificados CA, más los paquetes de
`requirements.txt` (listarlos con `docker compose exec lab pip list`; incluye DuckDB y `requests`).

**Contenedor `metabase`** (`eclipse-temurin:21-jre-jammy`, Debian): Java 21, Metabase v0.63.19 y el driver de DuckDB 1.5.5.0
instalado como plugin. Se usa Debian en lugar de la imagen oficial (Alpine) porque la librería nativa del driver requiere glibc.

Nota de compatibilidad: la versión de `duckdb` de `requirements.txt` debe estar alineada con la del driver
(1.5.x), porque Metabase abre el mismo archivo `.duckdb` que crea Python.

Versiones reales dentro del contenedor `lab` (`docker compose exec lab pip list`):

| Paquete | Versión |
|---|---|
| Python | 3.11.14 |
| duckdb | 1.5.5 |
| jupyterlab | 4.6.4 |
| ipykernel | 7.4.0 |
| nbconvert | 7.17.1 |
| pandas | 3.0.6 |
| numpy | 2.4.6 |
| pyarrow | 25.0.1 |
| matplotlib | 3.11.2 |
| requests | 2.34.2 |

`ipykernel`, `nbconvert` y `numpy` llegan como dependencias de JupyterLab y pandas.

## 1.6 Por qué es importante un ambiente reproducible en análisis de datos

Un resultado analítico solo es confiable si otra persona (o uno mismo, meses después) puede obtenerlo de nuevo.
Un ambiente reproducible fija las versiones de Python, DuckDB y Metabase, así que el mismo código produce los mismos
resultados en cualquier máquina del equipo y se evitan los problemas del tipo "en mi computadora funciona". Además:
facilita incorporar a un nuevo integrante en minutos, permite auditar y corregir errores rastreando exactamente
cómo se generó un número, hace comparables los benchmarks (mismas versiones y configuración) y deja el análisis
listo para automatizarse en un entorno de producción. Aquí esto se combina con datos fuera de Git, descarga por
script y SQL versionado, de modo que todo el flujo (datos → base → indicadores) se puede regenerar desde cero.
