"""Utilidades compartidas por build_db.py y benchmark.py.

Los archivos de yellow y green no tienen el mismo esquema (tpep_* vs lpep_*,
columnas que solo existen en un tipo o que aparecen en anios recientes, como
cbd_congestion_fee). Este modulo genera una unica sentencia SELECT que:

  * lee los Parquet con union_by_name (tolera columnas faltantes entre archivos),
  * renombra las columnas a un esquema comun en minusculas,
  * convierte los tipos de forma explicita (TRY_CAST: un valor no convertible
    pasa a NULL en lugar de abortar la carga),
  * agrega taxi_type y columnas de trazabilidad (source_file/year/month).

Esa misma sentencia se usa para (a) materializar la tabla `trips` y (b) crear la
vista sobre los Parquet en el benchmark, de modo que ambas estrategias
devuelvan exactamente las mismas columnas y las consultas sean identicas.
"""

import glob
import os
import re
from pathlib import Path

TIPOS_TAXI = ("yellow", "green")
REPO_ROOT = Path(__file__).resolve().parent.parent
ARCHIVO_RE = re.compile(r"^(yellow|green)_tripdata_(\d{4})-(\d{2})\.parquet$")


def data_dir() -> Path:
    """Carpeta data/. Dentro del contenedor es /workspace/data. Se puede forzar con LAB_DATA_DIR."""
    return Path(os.environ.get("LAB_DATA_DIR", REPO_ROOT / "data")).resolve()


def db_por_defecto() -> Path:
    return data_dir() / "processed" / "taxi.duckdb"


# (columna destino, tipo, nombres posibles en el origen, en minusculas)
COLUMNAS = [
    ("vendor_id", "INTEGER", ["vendorid"]),
    ("pickup_datetime", "TIMESTAMP", ["tpep_pickup_datetime", "lpep_pickup_datetime"]),
    ("dropoff_datetime", "TIMESTAMP", ["tpep_dropoff_datetime", "lpep_dropoff_datetime"]),
    ("passenger_count", "INTEGER", ["passenger_count"]),
    ("trip_distance", "DOUBLE", ["trip_distance"]),
    ("ratecode_id", "INTEGER", ["ratecodeid"]),
    ("store_and_fwd_flag", "VARCHAR", ["store_and_fwd_flag"]),
    ("pu_location_id", "INTEGER", ["pulocationid"]),
    ("do_location_id", "INTEGER", ["dolocationid"]),
    ("payment_type", "INTEGER", ["payment_type"]),
    ("trip_type", "INTEGER", ["trip_type"]),                 # solo green
    ("fare_amount", "DOUBLE", ["fare_amount"]),
    ("extra", "DOUBLE", ["extra"]),
    ("mta_tax", "DOUBLE", ["mta_tax"]),
    ("tip_amount", "DOUBLE", ["tip_amount"]),
    ("tolls_amount", "DOUBLE", ["tolls_amount"]),
    ("ehail_fee", "DOUBLE", ["ehail_fee"]),                  # solo green
    ("improvement_surcharge", "DOUBLE", ["improvement_surcharge"]),
    ("congestion_surcharge", "DOUBLE", ["congestion_surcharge"]),
    ("airport_fee", "DOUBLE", ["airport_fee"]),              # solo yellow
    ("cbd_congestion_fee", "DOUBLE", ["cbd_congestion_fee"]),  # anios recientes
    ("total_amount", "DOUBLE", ["total_amount"]),
]

# Columnas de trazabilidad derivadas del nombre del archivo (no es f-string: hay llaves de regex)
_SQL_TRAZABILIDAD = (
    r"    regexp_extract(filename, '[^/\\]+$') AS source_file," "\n"
    r"    CAST(regexp_extract(filename, '(\d{4})-\d{2}\.parquet$', 1) AS SMALLINT) AS source_year," "\n"
    r"    CAST(regexp_extract(filename, '\d{4}-(\d{2})\.parquet$', 1) AS SMALLINT) AS source_month"
)


def _lit(texto) -> str:
    return "'" + str(texto).replace("'", "''") + "'"


def listar_archivos():
    """Lista [(tipo, anio, mes, Path)] de los Parquet en data/raw, ordenada."""
    res = []
    for tipo in TIPOS_TAXI:
        for ruta in glob.glob(str(data_dir() / "raw" / tipo / "*" / "*.parquet")):
            m = ARCHIVO_RE.match(Path(ruta).name)
            if m:
                res.append((m.group(1), int(m.group(2)), int(m.group(3)), Path(ruta)))
    return sorted(res, key=lambda x: (x[1], x[2], x[0]))


def fuentes_glob(years=None):
    """Patrones glob por tipo de taxi (todos los anios, o solo `years`). Omite patrones sin archivos."""
    raw = data_dir() / "raw"
    res = {}
    for tipo in TIPOS_TAXI:
        if years:
            patrones = [str(raw / tipo / str(y) / "*.parquet") for y in years]
        else:
            patrones = [str(raw / tipo / "*" / "*.parquet")]
        res[tipo] = [p for p in patrones if glob.glob(p)]
    return res


def select_normalizado(con, tipo: str, fuentes):
    """SELECT normalizado para un tipo de taxi. Devuelve (sql, columnas_sin_mapear)."""
    origen = "read_parquet([" + ", ".join(_lit(f) for f in fuentes) + "], union_by_name=true, filename=true)"
    descr = [fila[0] for fila in con.execute(f"DESCRIBE SELECT * FROM {origen}").fetchall()]

    por_minuscula = {}
    for nombre in descr:
        por_minuscula.setdefault(nombre.lower(), []).append(nombre)

    usadas, exprs = set(), []
    for destino, tipo_sql, candidatas in COLUMNAS:
        presentes = [c for cand in candidatas for c in por_minuscula.get(cand, [])]
        if presentes:
            usadas.update(presentes)
            partes = [f'TRY_CAST("{c}" AS {tipo_sql})' for c in presentes]
            expr = partes[0] if len(partes) == 1 else "COALESCE(" + ", ".join(partes) + ")"
        else:
            expr = f"CAST(NULL AS {tipo_sql})"
        exprs.append(f"    {expr} AS {destino}")

    sin_mapear = sorted(c for c in descr if c not in usadas and c != "filename")
    sql = (
        "SELECT\n"
        f"    {_lit(tipo)} AS taxi_type,\n"
        + ",\n".join(exprs) + ",\n"
        + _SQL_TRAZABILIDAD + "\n"
        f"FROM {origen}"
    )
    return sql, sin_mapear


def normalizado_sql(con, fuentes_por_tipo):
    """SELECT con UNION ALL de todos los tipos que tengan fuentes. Devuelve (sql, {tipo: sin_mapear})."""
    partes, avisos = [], {}
    for tipo in TIPOS_TAXI:
        fuentes = fuentes_por_tipo.get(tipo) or []
        if not fuentes:
            continue
        sql, sin_mapear = select_normalizado(con, tipo, fuentes)
        partes.append(sql)
        avisos[tipo] = sin_mapear
    if not partes:
        raise FileNotFoundError("No hay archivos Parquet. Ejecute primero: python scripts/download_data.py")
    return "\nUNION ALL\n".join(partes), avisos
