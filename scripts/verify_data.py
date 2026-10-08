#!/usr/bin/env python3
"""Verifica que el conjunto de datos descargado este completo e integro.

Para cada tipo de taxi (yellow/green), anio y mes comprueba:
  1. Si el servidor de la TLC publica el archivo (HEAD, sin descargar).
  2. Si existe localmente y su tamanio coincide con el del servidor.
  3. Si el Parquet es legible (se lee el footer con DuckDB) y cuantas filas tiene.

Estados:
  OK            archivo local presente, integro y legible
  FALTA         publicado por la TLC pero no esta en disco  -> volver a descargar
  INVALIDO      existe pero su tamanio no coincide o no es un Parquet legible
  NO_PUBLICADO  aun no existe en la fuente (esperado para meses recientes)
  ERROR_RED     no se pudo consultar al servidor
  AUSENTE       (solo con --offline) no esta en disco; no se sabe si existe en la fuente

Ademas se reportan como TEMPORAL los archivos .part de descargas interrumpidas.

Uso:
    python scripts/verify_data.py
    python scripts/verify_data.py --years 2026
    python scripts/verify_data.py --offline          # sin consultar la red
    python scripts/verify_data.py --delete-invalid   # borra archivos INVALIDO y .part

Escribe el inventario en docs/data_inventory.csv (evidencia para el punto 2.7).
Codigo de salida: 0 si todo lo publicado esta presente y es valido; 1 en otro caso.
"""

import argparse
import csv
import sys
from collections import defaultdict
from pathlib import Path

import duckdb

import download_data as dd

MALOS = {"FALTA", "INVALIDO", "ERROR_RED"}


def filas_parquet(con, ruta: Path):
    """Numero de filas segun el footer del Parquet, o None si no es legible."""
    ruta_sql = str(ruta).replace("'", "''")
    try:
        return con.execute(f"SELECT num_rows FROM parquet_file_metadata('{ruta_sql}')").fetchone()[0]
    except duckdb.Error:
        return None


def main() -> int:
    p = argparse.ArgumentParser(description="Verifica la completitud de los datos descargados.")
    p.add_argument("--taxi", choices=(*dd.TIPOS_TAXI, "all"), default="all")
    p.add_argument("--years", type=int, nargs="+", default=list(dd.ANIOS_POR_DEFECTO))
    p.add_argument("--offline", action="store_true", help="no consultar al servidor")
    p.add_argument("--delete-invalid", action="store_true", help="borrar archivos INVALIDO y .part")
    p.add_argument("--out", default="docs/data_inventory.csv")
    a = p.parse_args()

    tipos = dd.TIPOS_TAXI if a.taxi == "all" else (a.taxi,)
    anios = sorted(set(a.years))
    con = duckdb.connect()
    filas = []

    for tipo in tipos:
        for anio in anios:
            for mes in range(1, 13):
                ruta = dd.ruta_destino(tipo, anio, mes)
                existe = ruta.exists()
                bytes_local = ruta.stat().st_size if existe else None
                if a.offline:
                    estado_srv, bytes_srv = None, None
                else:
                    estado_srv, bytes_srv = dd.consultar_servidor(dd.construir_url(tipo, anio, mes))

                n_filas = None
                if existe:
                    n_filas = filas_parquet(con, ruta)
                    if n_filas is None or (bytes_srv is not None and bytes_srv != bytes_local):
                        estado = "INVALIDO"
                        if a.delete_invalid:
                            ruta.unlink()
                    else:
                        estado = "OK"
                elif a.offline:
                    estado = "AUSENTE"
                elif estado_srv == "publicado":
                    estado = "FALTA"
                elif estado_srv == "no_publicado":
                    estado = "NO_PUBLICADO"
                else:
                    estado = "ERROR_RED"

                filas.append({
                    "taxi": tipo, "anio": anio, "mes": mes, "archivo": ruta.name,
                    "estado": estado, "bytes_local": bytes_local, "bytes_servidor": bytes_srv,
                    "filas": n_filas,
                })

    # Archivos temporales de descargas interrumpidas
    temporales = sorted(dd.DIR_DESTINO.glob(f"**/*{dd.SUFIJO_TEMPORAL}")) if dd.DIR_DESTINO.exists() else []
    for t in temporales:
        print(f"TEMPORAL: {t}")
        if a.delete_invalid:
            t.unlink()
    n_temporales = 0 if a.delete_invalid else len(temporales)

    # --- Resumen por tipo y anio
    res = defaultdict(lambda: defaultdict(int))
    for f in filas:
        k = (f["taxi"], f["anio"])
        res[k][f["estado"]] += 1
        res[k]["filas"] += f["filas"] or 0
    print(f"\n{'taxi':8}{'anio':6}{'OK':>4}{'FALTA':>7}{'INVAL':>7}{'NO_PUB':>8}{'RED':>5}{'AUS':>5}{'filas':>16}")
    for (tipo, anio), r in sorted(res.items()):
        print(f"{tipo:8}{anio:<6}{r['OK']:>4}{r['FALTA']:>7}{r['INVALIDO']:>7}"
              f"{r['NO_PUBLICADO']:>8}{r['ERROR_RED']:>5}{r['AUSENTE']:>5}{r['filas']:>16,}")

    total_ok = sum(1 for f in filas if f["estado"] == "OK")
    total_filas = sum(f["filas"] or 0 for f in filas)
    print(f"\nArchivos OK: {total_ok}   Filas totales: {total_filas:,}   Temporales: {n_temporales}")

    problemas = [f for f in filas if f["estado"] in MALOS]
    for f in problemas:
        print(f"  {f['estado']:10} {f['taxi']} {f['anio']}-{f['mes']:02d}")
    if a.offline and any(f["estado"] == "AUSENTE" for f in filas):
        print("\nNota: en modo --offline no se puede distinguir un mes faltante de uno aun no publicado.")

    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(filas[0].keys()))
        w.writeheader()
        w.writerows(filas)
    print(f"\nInventario escrito en {out}")

    return 1 if (problemas or n_temporales) else 0


if __name__ == "__main__":
    sys.exit(main())
