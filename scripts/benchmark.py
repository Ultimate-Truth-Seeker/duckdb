#!/usr/bin/env python3
"""Benchmark: consultar Parquet directamente vs. tabla materializada en DuckDB (Ejercicio 6).

Metodologia
  * Las MISMAS consultas (sql/04_benchmark/q*.sql) se ejecutan sobre una relacion llamada
    `trips` en dos conexiones distintas:
      - parquet: vista temporal con la sentencia normalizada de taxi_common.py leyendo los
        archivos Parquet (mismo esquema y tipos que la tabla -> comparacion valida).
      - tabla:   vista temporal sobre trips de la base materializada (ATTACH ... READ_ONLY).
  * Escalas de datos: los primeros N meses cronologicos disponibles (yellow+green).
  * Por consulta se ejecuta `--runs` veces: se reporta la primera ejecucion, la mediana de las
    ejecuciones y la minima. Se materializa todo el resultado (fetchall) dentro del tiempo medido.
  * Se verifica que ambas estrategias devuelvan el mismo resultado (tolerancia relativa 1e-6).
  * Cada estrategia usa su propia conexion y se ejecutan una despues de otra (no en paralelo).

Limitaciones: no se puede vaciar la cache del sistema de archivos desde el contenedor, por lo que la
"primera ejecucion" no es necesariamente en frio absoluto. En Docker Desktop (Windows/macOS) las carpetas
montadas son mas lentas que el disco interno; considerelo al interpretar los tiempos.

Uso (dentro del contenedor, despues de scripts/build_db.py):
    python scripts/benchmark.py
    python scripts/benchmark.py --scales 1,6,all --runs 3
    python scripts/benchmark.py --threads 4 --memory-limit 4GB

Salida: docs/benchmark_results.csv y docs/benchmark_results.md
"""

import argparse
import csv
import os
import statistics
import sys
import time
from pathlib import Path

import duckdb

import taxi_common as tc


def cargar_consultas(directorio: Path):
    archivos = sorted(directorio.glob("q*.sql"))
    if not archivos:
        sys.exit(f"No hay consultas q*.sql en {directorio}")
    return [(f.stem, f.read_text(encoding="utf-8")) for f in archivos]


def _igual(x, y, tol=1e-6) -> bool:
    if isinstance(x, (list, tuple)) and isinstance(y, (list, tuple)):
        return len(x) == len(y) and all(_igual(a, b, tol) for a, b in zip(x, y))
    if isinstance(x, float) or isinstance(y, float):
        if x is None or y is None:
            return x is y
        return abs(x - y) <= tol * max(1.0, abs(x), abs(y))
    return x == y


def definir_escalas(meses, texto):
    """'1,3,6,all' -> lista ordenada de cantidades de meses sin repetir."""
    escalas = []
    for tok in (t.strip() for t in texto.split(",") if t.strip()):
        n = len(meses) if tok == "all" else min(int(tok), len(meses))
        if n > 0 and n not in escalas:
            escalas.append(n)
    return sorted(escalas)


def nueva_conexion(args):
    con = duckdb.connect()
    if args.threads:
        con.execute(f"SET threads = {int(args.threads)}")
    if args.memory_limit:
        con.execute(f"SET memory_limit = '{args.memory_limit}'")
    return con


def correr(con, consultas, runs):
    """Devuelve {consulta: (tiempos, resultado_primera_ejecucion)}."""
    salida = {}
    for nombre, sql in consultas:
        tiempos, primero = [], None
        for i in range(runs):
            t = time.perf_counter()
            filas = con.execute(sql).fetchall()
            tiempos.append(time.perf_counter() - t)
            if i == 0:
                primero = filas
        salida[nombre] = (tiempos, primero)
        print(f"      {nombre:34} primera {tiempos[0]:8.3f}s   mediana {statistics.median(tiempos):8.3f}s")
    return salida


def resumir(tiempos):
    return tiempos[0], statistics.median(tiempos), min(tiempos)


def main() -> int:
    p = argparse.ArgumentParser(description="Benchmark Parquet vs tabla DuckDB.")
    p.add_argument("--db", default=str(tc.db_por_defecto()))
    p.add_argument("--queries-dir", default=str(tc.REPO_ROOT / "sql" / "04_benchmark"))
    p.add_argument("--out-dir", default=str(tc.REPO_ROOT / "docs"))
    p.add_argument("--scales", default="1,3,6,12,24,all",
                   help="cantidades de meses separadas por coma, o 'all' (por defecto: 1,3,6,12,24,all)")
    p.add_argument("--runs", type=int, default=5, help="ejecuciones por consulta (por defecto 5)")
    p.add_argument("--threads", type=int)
    p.add_argument("--memory-limit")
    args = p.parse_args()

    if not os.path.exists(args.db):
        sys.exit(f"No existe {args.db}. Ejecute primero: python scripts/build_db.py")
    archivos = tc.listar_archivos()
    if not archivos:
        sys.exit("No hay archivos Parquet en data/raw. Ejecute primero: python scripts/download_data.py")

    consultas = cargar_consultas(Path(args.queries_dir))
    meses = sorted({(a, m) for _, a, m, _ in archivos})
    escalas = definir_escalas(meses, args.scales)

    # Metadatos del entorno
    con_info = duckdb.connect(args.db, read_only=True)
    build = dict(con_info.execute("SELECT key, value FROM build_info").fetchall())
    con_info.close()
    tam_db_gb = os.path.getsize(args.db) / 1024**3
    entorno = {
        "duckdb": duckdb.__version__,
        "cpus": os.cpu_count(),
        "threads": args.threads or "por defecto",
        "memory_limit": args.memory_limit or "por defecto",
        "runs": args.runs,
        "build_seconds": build.get("build_seconds"),
        "db_gb": round(tam_db_gb, 2),
    }
    print(f"Entorno: {entorno}")

    resultados = []
    for n in escalas:
        elegidos = set(meses[:n])
        sel = [(t, a, m, ruta) for t, a, m, ruta in archivos if (a, m) in elegidos]
        nombres = [ruta.name for *_, ruta in sel]
        gb_parquet = sum(ruta.stat().st_size for *_, ruta in sel) / 1024**3
        print(f"\n=== Escala: {n} mes(es) | {len(sel)} archivos | {gb_parquet:.2f} GiB Parquet ===")

        # --- Estrategia 1: Parquet directo
        print("    [parquet]")
        con = nueva_conexion(args)
        fuentes = {t: [str(r) for tt, _, _, r in sel if tt == t] for t in tc.TIPOS_TAXI}
        sql_vista, _ = tc.normalizado_sql(con, fuentes)
        con.execute(f"CREATE TEMP VIEW trips AS {sql_vista}")
        filas_escala = con.execute("SELECT count(*) FROM trips").fetchone()[0]
        res_pq = correr(con, consultas, args.runs)
        con.close()

        # --- Estrategia 2: tabla materializada
        print("    [tabla]")
        con = nueva_conexion(args)
        con.execute(f"ATTACH '{args.db}' AS tdb (READ_ONLY)")
        if n == len(meses):
            con.execute("CREATE TEMP VIEW trips AS SELECT * FROM tdb.trips")
        else:
            lista = ", ".join("'" + x.replace("'", "''") + "'" for x in nombres)
            con.execute(f"CREATE TEMP VIEW trips AS SELECT * FROM tdb.trips WHERE source_file IN ({lista})")
        res_tb = correr(con, consultas, args.runs)
        con.close()

        for nombre, _ in consultas:
            t_pq, r_pq = res_pq[nombre]
            t_tb, r_tb = res_tb[nombre]
            equivalente = _igual(r_pq, r_tb)
            if not equivalente:
                print(f"    AVISO: resultados distintos entre estrategias en {nombre}")
            for fuente, tiempos in (("parquet", t_pq), ("tabla", t_tb)):
                primera, mediana, minima = resumir(tiempos)
                resultados.append({
                    "escala_meses": n, "archivos": len(sel), "gb_parquet": round(gb_parquet, 3),
                    "filas": filas_escala, "consulta": nombre, "fuente": fuente,
                    "primera_s": round(primera, 4), "mediana_s": round(mediana, 4),
                    "minima_s": round(minima, 4), "ejecuciones": len(tiempos),
                    "resultado_equivalente": equivalente,
                })

    # --- CSV
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    csv_path = out / "benchmark_results.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(resultados[0].keys()))
        w.writeheader()
        w.writerows(resultados)

    # --- Markdown (tabla comparativa)
    idx = {(r["escala_meses"], r["consulta"], r["fuente"]): r for r in resultados}
    lineas = [
        "# Resultados del benchmark: Parquet directo vs tabla DuckDB",
        "",
        "Generado por `scripts/benchmark.py`. Tiempos en segundos (mediana de las ejecuciones; "
        "entre parentesis, la primera ejecucion).",
        "",
        "Entorno: " + ", ".join(f"{k}={v}" for k, v in entorno.items()),
        "",
        "| Meses | Archivos | GiB Parquet | Filas | Consulta | Parquet (s) | Tabla (s) | Parquet / Tabla | Resultados iguales |",
        "|---:|---:|---:|---:|---|---:|---:|---:|:-:|",
    ]
    for n in escalas:
        for nombre, _ in consultas:
            a, b = idx[(n, nombre, "parquet")], idx[(n, nombre, "tabla")]
            razon = a["mediana_s"] / b["mediana_s"] if b["mediana_s"] > 0 else float("nan")
            lineas.append(
                f"| {n} | {a['archivos']} | {a['gb_parquet']} | {a['filas']:,} | {nombre} | "
                f"{a['mediana_s']:.3f} ({a['primera_s']:.3f}) | {b['mediana_s']:.3f} ({b['primera_s']:.3f}) | "
                f"{razon:.2f}x | {'si' if a['resultado_equivalente'] else 'NO'} |"
            )
    lineas += [
        "",
        f"Tiempo de construccion de la tabla materializada: {build.get('build_seconds')} s; "
        f"tamanio del archivo .duckdb: {entorno['db_gb']} GiB.",
        "",
        "`Parquet / Tabla` > 1 significa que la tabla materializada fue mas rapida.",
    ]
    md_path = out / "benchmark_results.md"
    md_path.write_text("\n".join(lineas) + "\n", encoding="utf-8")

    print(f"\nResultados: {csv_path}\n            {md_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
