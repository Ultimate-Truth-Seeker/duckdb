# Sistema de descarga de datos (Ejercicios 2, 5 y 8)

Scripts: `scripts/download_data.py` (descarga) y `scripts/verify_data.py` (verificación).

## 2.1 Análisis del script original

El script proporcionado ya tenía la lógica de red (consulta de meses publicados, descarga a archivo
temporal, reintentos, omisión de archivos existentes), pero estaba **fijo a 2026**: la constante
`ANIO = 2026` se usaba dentro de `construir_nombre`, `construir_url` y `ruta_destino`. Esa constante era
la parte que debía modificarse para poder incorporar 2024 y 2025 (ejercicios 5 y 8) sin duplicar código.

## 2.6 Cambios realizados al script

| # | Cambio | Motivo |
|---|--------|--------|
| 1 | `ANIO` constante → argumento `--years` (por defecto 2024, 2025, 2026); `construir_nombre`, `construir_url` y `ruta_destino` reciben `anio`. | Incorporar nuevos años sin tocar el código (5.1, 8.1). |
| 2 | `esta_publicado()` (bool) → `consultar_servidor()` que devuelve `publicado` / `no_publicado` (403/404) / `error`. | El original trataba cualquier fallo de red como "aún no publicado": un mes podía quedar sin descargar sin que nadie lo notara. Ahora un error de red cuenta como fallido y se reintenta en la siguiente ejecución. |
| 3 | Se valida que los bytes descargados coincidan con `Content-Length`. | Detecta descargas cortadas que de otro modo quedarían como archivos "válidos" pero incompletos. |
| 4 | Cabecera `Accept-Encoding: identity`. | Para que el tamaño en bytes sea comparable con `Content-Length`. |
| 5 | Opción `--dry-run` y variable de entorno `TLC_BASE_URL`. | Ver qué se descargaría sin descargar; permitir pruebas contra un servidor local. |
| 6 | Resumen final por tipo/año y sugerencia de ejecutar `verify_data.py`. | Trazabilidad. |

Se conserva sin cambios: estructura `data/raw/<tipo>/<año>/`, omisión de archivos existentes (2.4, 5.3, 8.2),
descarga a `.part` con renombrado atómico y 3 reintentos por archivo.

## Uso

```bash
# Dentro del contenedor (docker compose exec lab ...)
python scripts/download_data.py                  # yellow + green, 2024-2026
python scripts/download_data.py --years 2026     # solo 2026 (Ejercicio 2)
python scripts/download_data.py --years 2024     # agrega 2024 (Ejercicio 5); 2026 se conserva
python scripts/download_data.py --dry-run        # solo informa
python scripts/verify_data.py                    # verifica y escribe docs/data_inventory.csv
```

## 2.7 ¿Cómo se determinó que el conjunto descargado está completo?

"Completo" se define frente a la **fuente**, no frente a una cuenta fija de 12 meses, porque la TLC publica con
retraso. `scripts/verify_data.py` comprueba para cada combinación tipo × año × mes (72 combinaciones para
2 tipos × 3 años × 12 meses):

1. **Publicación:** consulta al servidor (HEAD) si el archivo existe. Un mes `NO_PUBLICADO` es esperado y no es un error.
2. **Presencia:** todo mes publicado debe existir en disco (`FALTA` en caso contrario).
3. **Integridad de tamaño:** el tamaño local debe ser igual al `Content-Length` del servidor.
4. **Legibilidad:** el footer del Parquet debe poder leerse con DuckDB (un archivo truncado no tiene footer válido); de ahí se obtiene también el número de filas.
5. **Sin temporales:** no deben quedar archivos `.part`.

El resultado queda en `docs/data_inventory.csv` (una fila por archivo con estado, bytes y filas), que sirve de evidencia.
El script termina con código 0 solo si no hay `FALTA`, `INVALIDO` ni `ERROR_RED`.

Esta lógica se probó con archivos sintéticos: un archivo truncado se reporta como `INVALIDO`, uno borrado como
`FALTA`, y tras `--delete-invalid` más una nueva descarga la verificación termina limpia.

### Resultado de la ejecución real

Descarga y verificación del 2026-10-08 (`download_data.py` y luego `verify_data.py`, ambos con código de salida 0):

```text
taxi    anio    OK  FALTA  INVAL  NO_PUB  RED  AUS           filas
green   2024    12      0      0       0    0    0         660,218
green   2025    12      0      0       0    0    0         591,375
green   2026     8      0      0       4    0    0         337,114
yellow  2024    12      0      0       0    0    0      41,169,720
yellow  2025    12      0      0       0    0    0      48,722,602
yellow  2026     8      0      0       4    0    0      29,703,355

Archivos OK: 64   Filas totales: 121,184,384   Temporales: 0
```

- La descarga bajó 64 archivos, 0 fallidos, ~2.0 GB en `data/raw/`.
- Meses de 2026 **no publicados** por la TLC en esa fecha: septiembre a diciembre, en yellow y en green (8 archivos). Es lo esperado, no un error.
- Las 121,184,384 filas del inventario (`docs/data_inventory.csv`) coinciden con las de la tabla `trips` construida después (`v08` devuelve 0 filas).

## 5.9 Características del diseño que permiten incorporar nuevos archivos

- **Convención de rutas:** `data/raw/<tipo>/<año>/<archivo>.parquet`. Agregar datos es solo agregar archivos en esa estructura.
- **Parametrización por año:** un año nuevo se incorpora con `--years`, sin editar código.
- **Idempotencia:** lo que ya existe no se vuelve a descargar; se puede re-ejecutar siempre.
- **Lectura por comodines:** `build_db.py` y las consultas leen `data/raw/<tipo>/*/*.parquet`, por lo que un año nuevo entra automáticamente al análisis.
- **Esquema tolerante:** `union_by_name=true` y el mapeo de columnas de `scripts/taxi_common.py` absorben columnas que aparecen o desaparecen entre años (p. ej. `cbd_congestion_fee`, `Airport_fee`/`airport_fee`).
