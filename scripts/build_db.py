#!/usr/bin/env python3
"""Materializa los Parquet de data/raw en una base DuckDB (data/processed/taxi.duckdb).

Crea:
  trips        tabla unificada yellow+green con esquema normalizado (ver taxi_common.py)
  ingest_log   una fila por archivo fuente: filas, fecha minima y maxima de recogida
  build_info   metadatos de la construccion (fecha, version de DuckDB, tiempo, filas)

La construccion se hace en un archivo temporal y solo se reemplaza la base final al
terminar con exito, de modo que una falla no deja una base a medias.

La sentencia SQL generada queda registrada en sql/00_build/create_trips.sql
(requisito: toda transformacion sobre los datos debe quedar registrada).

Uso (dentro del contenedor):
    python scripts/build_db.py
    python scripts/build_db.py --years 2026            # solo algunos anios
    python scripts/build_db.py --memory-limit 4GB --threads 4

IMPORTANTE: un .duckdb admite un solo proceso con permiso de escritura. Antes de
reconstruir, detenga Metabase (docker compose stop metabase) y cierre los notebooks que
tengan la base abierta; despues reinicie Metabase.
"""

import argparse
import os
import sys
import time
from datetime import datetime, timezone

import duckdb

import taxi_common as tc


def main() -> int:
    p = argparse.ArgumentParser(description="Construye la tabla materializada de DuckDB.")
    p.add_argument("--db", default=str(tc.db_por_defecto()), help="ruta del archivo .duckdb")
    p.add_argument("--years", type=int, nargs="+", help="solo estos anios (por defecto: todos los descargados)")
    p.add_argument("--threads", type=int)
    p.add_argument("--memory-limit", help="p. ej. 4GB")
    p.add_argument("--sql-out", default=str(tc.REPO_ROOT / "sql" / "00_build" / "create_trips.sql"))
    a = p.parse_args()

    db = os.path.abspath(a.db)
    tmp = db + ".tmp"
    os.makedirs(os.path.dirname(db), exist_ok=True)
    for sufijo in ("", ".wal"):
        if os.path.exists(tmp + sufijo):
            os.remove(tmp + sufijo)

    t0 = time.perf_counter()
    con = duckdb.connect(tmp)
    con.execute("SET preserve_insertion_order = false")   # reduce memoria en cargas grandes
    if a.threads:
        con.execute(f"SET threads = {int(a.threads)}")
    if a.memory_limit:
        con.execute(f"SET memory_limit = '{a.memory_limit}'")

    fuentes = tc.fuentes_glob(a.years)
    try:
        select, avisos = tc.normalizado_sql(con, fuentes)
    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        return 1
    for tipo, sin_mapear in avisos.items():
        if sin_mapear:
            print(f"AVISO ({tipo}): columnas de origen no incorporadas a la tabla: {sin_mapear}")

    ctas = f"CREATE TABLE trips AS\n{select};\n"
    os.makedirs(os.path.dirname(a.sql_out), exist_ok=True)
    with open(a.sql_out, "w", encoding="utf-8") as fh:
        fh.write(
            "-- GENERADO por scripts/build_db.py: no editar a mano.\n"
            "-- Materializa los Parquet de yellow y green en una tabla unica con esquema normalizado.\n"
            "-- Transformaciones: renombrado a esquema comun, TRY_CAST explicito de tipos,\n"
            "-- columnas ausentes en un tipo/anio -> NULL, trazabilidad por archivo (source_*).\n"
            "-- No se filtra ni se corrige ningun registro: la limpieza queda para el analisis.\n"
            f"-- Fuentes: {fuentes}\n\n" + ctas
        )
    print(f"SQL registrado en {a.sql_out}")

    print("Materializando tabla trips (puede tardar varios minutos)...")
    con.execute(ctas)
    n_filas = con.execute("SELECT count(*) FROM trips").fetchone()[0]

    con.execute("""
        CREATE TABLE ingest_log AS
        SELECT taxi_type, source_file, source_year, source_month,
               count(*) AS n_rows,
               min(pickup_datetime) AS min_pickup,
               max(pickup_datetime) AS max_pickup
        FROM trips
        GROUP BY ALL
        ORDER BY taxi_type, source_year, source_month
    """)
    n_archivos = con.execute("SELECT count(*) FROM ingest_log").fetchone()[0]

    segundos = time.perf_counter() - t0
    con.execute("CREATE TABLE build_info (key VARCHAR, value VARCHAR)")
    info = {
        "built_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "duckdb_version": duckdb.__version__,
        "build_seconds": f"{segundos:.1f}",
        "n_rows": str(n_filas),
        "n_files": str(n_archivos),
        "years": ",".join(map(str, a.years)) if a.years else "all",
    }
    con.executemany("INSERT INTO build_info VALUES (?, ?)", list(info.items()))
    con.execute("CHECKPOINT")
    con.close()

    os.replace(tmp, db)
    tam = os.path.getsize(db) / 1024**3
    print(f"\nListo: {db}")
    print(f"  filas        : {n_filas:,}")
    print(f"  archivos     : {n_archivos}")
    print(f"  tamanio .duckdb: {tam:.2f} GiB")
    print(f"  tiempo       : {segundos:.1f} s")
    print("Si Metabase estaba detenido, reinicielo: docker compose start metabase")
    return 0


if __name__ == "__main__":
    sys.exit(main())
