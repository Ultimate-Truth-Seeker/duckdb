#!/usr/bin/env python3
"""Ejecuta las consultas de sql/01_exploracion, 02_eda y 03_validacion_anios y documenta cada una.

Para cada archivo .sql escribe en el Markdown de salida lo que piden los puntos 3.8, 4.3, 5.8 y 8.7:
la consulta SQL, su objetivo, los archivos fuente, el resultado obtenido (primeras filas), el tiempo
y la decision tomada a partir del resultado.

Convencion de comentarios al inicio de cada .sql (todos opcionales salvo Objetivo):
    -- Objetivo: ...        (puede ocupar varias lineas de comentario)
    -- Fuente: ...
    -- Requiere: tabla     (solo se ejecuta con --source tabla)
    -- Decision: ...        (se escribe a mano DESPUES de ver el resultado y se vuelve a ejecutar este script)

La vista `trips` se construye igual que en el benchmark (scripts/taxi_common.py):
    --source parquet   lee directamente los Parquet de data/raw (por defecto)
    --source tabla     usa la tabla trips de data/processed/taxi.duckdb (solo lectura)

Tambien sirve para 5.7 y 8.3: si al agregar anios alguna consulta falla, el script termina con codigo 1
y la tabla resumen indica cual. Las consultas no se modifican al agregar anios.

Uso (dentro del contenedor):
    python scripts/document_queries.py
    python scripts/document_queries.py --source tabla --out docs/consultas_resultados_tabla.md
    python scripts/document_queries.py --dirs 01_exploracion --max-rows 30
"""

import argparse
import re
import sys
import time
from datetime import datetime
from pathlib import Path

import duckdb

import taxi_common as tc

DIRS = ["01_exploracion", "02_eda", "03_validacion_anios"]
TITULOS = {"01_exploracion": "Exploracion con Parquet directo (Ej. 3)",
           "02_eda": "Analisis exploratorio (Ej. 4)",
           "03_validacion_anios": "Validacion al incorporar anios (Ej. 5 y 8.3)"}


def cabecera(texto):
    """Devuelve dict con objetivo, fuente y decision leidos de los comentarios iniciales."""
    campos, actual = {}, None
    for linea in texto.splitlines():
        if not linea.startswith("--"):
            break
        cuerpo = linea[2:].strip()
        m = re.match(r"(Objetivo|Fuente|Requiere|Decision):\s*(.*)", cuerpo)
        if m:
            actual = m.group(1).lower()
            campos[actual] = m.group(2)
        elif actual and cuerpo:
            campos[actual] += " " + cuerpo
    return campos


def celda(v):
    if v is None:
        return ""
    if isinstance(v, float):
        return f"{v:,.4g}" if abs(v) >= 1e6 or (v != 0 and abs(v) < 1e-3) else f"{v:,.2f}"
    if isinstance(v, int) and not isinstance(v, bool):
        return f"{v:,}"
    return str(v).replace("|", "/").replace("\n", " ")


def tabla_md(columnas, filas):
    out = ["| " + " | ".join(columnas) + " |", "|" + "|".join("---" for _ in columnas) + "|"]
    out += ["| " + " | ".join(celda(v) for v in f) + " |" for f in filas]
    return "\n".join(out)


def abrir(source, db):
    con = duckdb.connect()
    if source == "tabla":
        con.execute(f"ATTACH '{db}' AS tdb (READ_ONLY)")
        for nombre in ("trips", "ingest_log", "build_info"):
            con.execute(f"CREATE TEMP VIEW {nombre} AS SELECT * FROM tdb.{nombre}")
    else:
        sql, _ = tc.normalizado_sql(con, tc.fuentes_glob())
        con.execute(f"CREATE TEMP VIEW trips AS {sql}")
    return con


def main() -> int:
    p = argparse.ArgumentParser(description="Ejecuta y documenta las consultas SQL del proyecto.")
    p.add_argument("--source", choices=["parquet", "tabla"], default="parquet")
    p.add_argument("--db", default=str(tc.db_por_defecto()))
    p.add_argument("--dirs", nargs="+", default=DIRS)
    p.add_argument("--max-rows", type=int, default=15, help="filas del resultado que se muestran (por defecto 15)")
    p.add_argument("--out", default=str(tc.REPO_ROOT / "docs" / "consultas_resultados.md"))
    a = p.parse_args()

    if a.source == "tabla" and not Path(a.db).exists():
        sys.exit(f"No existe {a.db}. Ejecute primero: python scripts/build_db.py")
    con = abrir(a.source, a.db)
    datos = tc.data_dir().as_posix()
    n_archivos = len(tc.listar_archivos())

    secciones, resumen, fallas = [], [], 0
    for d in a.dirs:
        for f in sorted((tc.REPO_ROOT / "sql" / d).glob("*.sql")):
            texto = f.read_text(encoding="utf-8")
            h = cabecera(texto)
            if h.get("requiere") == "tabla" and a.source != "tabla":
                resumen.append((f"sql/{d}/{f.name}", "OMITIDA", 0, 0.0))
                print(f"OMIT  sql/{d}/{f.name} (requiere --source tabla)")
                continue
            t0 = time.perf_counter()
            try:
                cur = con.execute(texto.replace("/workspace/data", datos))
                cols = [c[0] for c in cur.description]
                filas = cur.fetchall()
                seg, estado, err = time.perf_counter() - t0, "OK", None
            except Exception as e:  # la consulta se reporta como fallida, no se detiene el resto
                seg, estado, err, filas, cols = time.perf_counter() - t0, "FALLA", str(e).splitlines()[0], [], []
                fallas += 1
            rel = f"sql/{d}/{f.name}"
            resumen.append((rel, estado, len(filas), seg))
            bloque = [f"### `{rel}`", "",
                      f"**Objetivo:** {h.get('objetivo', '(sin objetivo documentado)')}", "",
                      f"**Fuente:** {h.get('fuente', 'ver el SQL')}", "",
                      "**Consulta SQL:**", "", "```sql", texto.strip(), "```", ""]
            if err:
                bloque += [f"**Resultado:** ERROR: {err}", ""]
            else:
                bloque += [f"**Resultado** ({len(filas):,} filas; se muestran {min(len(filas), a.max_rows)}; {seg:.2f} s):", "",
                           tabla_md(cols, filas[:a.max_rows]), ""]
            bloque += [f"**Decision / interpretacion:** {h.get('decision', '_PENDIENTE: escribir `-- Decision:` en el .sql y volver a ejecutar este script._')}", ""]
            secciones.append((d, bloque))
            print(f"{estado:5} {rel:62} {len(filas):>6} filas {seg:7.2f}s")

    out = ["# Consultas documentadas con su resultado",
           "",
           f"Generado por `scripts/document_queries.py` el {datetime.now():%Y-%m-%d %H:%M}. "
           f"Fuente de datos: **{a.source}** ({n_archivos} archivos Parquet en `data/raw`). "
           "No editar a mano: la decision de cada consulta se escribe en su `.sql` (`-- Decision:`) y se regenera este archivo.",
           "", "## Resumen de ejecucion", "",
           tabla_md(["Consulta", "Estado", "Filas", "Segundos"], [(r, e, n, f"{s:.2f}") for r, e, n, s in resumen]), ""]
    for d in a.dirs:
        out += [f"## {TITULOS.get(d, d)}", ""]
        for dd, bloque in secciones:
            if dd == d:
                out += bloque
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"\nDocumentacion: {a.out}  |  fallas: {fallas}")
    return 1 if fallas else 0


if __name__ == "__main__":
    sys.exit(main())
