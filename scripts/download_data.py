#!/usr/bin/env python3
"""Descarga los archivos Parquet del NYC TLC Trip Record Data.

Descarga los registros de viajes de taxis amarillos (yellow) y verdes (green)
de los anios indicados con --years (por defecto 2024, 2025 y 2026).

Fuente oficial de los datos:
    https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page

Uso:
    python scripts/download_data.py                        # yellow+green, 2024-2026
    python scripts/download_data.py --years 2026           # solo 2026
    python scripts/download_data.py --years 2024 2025
    python scripts/download_data.py --taxi green --years 2025
    python scripts/download_data.py --dry-run              # solo informa, no descarga

Los archivos se guardan en:
    data/raw/<tipo>/<anio>/<nombre-original>.parquet

Comportamiento:
  - La TLC publica cada mes con varias semanas de atraso, por lo que no todos
    los meses del anio en curso existen todavia. El script consulta al servidor
    que meses estan publicados en lugar de suponerlos.
  - Un archivo que ya existe localmente no se vuelve a descargar.
  - La descarga se hace sobre un nombre temporal (.part) y solo se renombra al
    terminar, de modo que una interrupcion no deja archivos .parquet a medias.

Cambios respecto al script original del docente (ver tambien docs/descarga.md):
  1. El anio ya no es una constante (ANIO = 2026): se recibe con --years y las
     funciones construir_nombre/construir_url/ruta_destino reciben `anio`.
  2. La consulta al servidor (HEAD) distingue "no publicado" (403/404) de un
     error de red. Antes cualquier fallo de red se confundia con "aun no
     publicado" y un mes podia quedar sin descargar sin que nadie se enterara.
  3. Se valida el tamanio: lo descargado debe coincidir con el Content-Length
     anunciado por el servidor; si no, se reintenta (detecta cortes de red).
  4. Se pide `Accept-Encoding: identity` para que el tamanio en bytes sea
     comparable con Content-Length.
  5. Se agrega --dry-run y la variable de entorno TLC_BASE_URL (para pruebas
     contra un servidor local).
  6. El resumen final se reporta tambien por tipo y anio.
"""

import argparse
import os
import sys
from pathlib import Path

import requests

ANIOS_POR_DEFECTO = (2024, 2025, 2026)
TIPOS_TAXI = ("yellow", "green")
URL_BASE = os.environ.get("TLC_BASE_URL", "https://d37ci6vzurychx.cloudfront.net/trip-data")
DIR_DESTINO = Path("data/raw")

TIEMPO_ESPERA = 60          # segundos por peticion
INTENTOS = 3                # intentos por archivo antes de darse por vencido
BLOQUE = 1024 * 1024        # 1 MiB por bloque de descarga
SUFIJO_TEMPORAL = ".part"
CABECERAS = {"Accept-Encoding": "identity"}


def construir_nombre(tipo: str, anio: int, mes: int) -> str:
    """Nombre del archivo publicado por la TLC, p. ej. yellow_tripdata_2026-01.parquet."""
    return f"{tipo}_tripdata_{anio}-{mes:02d}.parquet"


def construir_url(tipo: str, anio: int, mes: int) -> str:
    """URL completa del archivo Parquet mensual."""
    return f"{URL_BASE}/{construir_nombre(tipo, anio, mes)}"


def ruta_destino(tipo: str, anio: int, mes: int) -> Path:
    """Ruta local donde se guarda el archivo."""
    return DIR_DESTINO / tipo / str(anio) / construir_nombre(tipo, anio, mes)


def consultar_servidor(url: str):
    """Consulta (sin descargar) si el archivo existe en el servidor.

    Devuelve (estado, tamanio):
      - ("publicado", bytes | None)  el archivo existe
      - ("no_publicado", None)       el servidor responde 403/404
      - ("error", None)              fallo de red u otra respuesta inesperada
    """
    try:
        r = requests.head(url, timeout=TIEMPO_ESPERA, allow_redirects=True, headers=CABECERAS)
    except requests.RequestException:
        return "error", None
    if r.status_code in (403, 404):
        return "no_publicado", None
    if not r.ok:
        return "error", None
    tam = r.headers.get("Content-Length")
    return "publicado", int(tam) if tam and tam.isdigit() else None


def formato_tamanio(n: float) -> str:
    for unidad in ("B", "KiB", "MiB", "GiB"):
        if n < 1024 or unidad == "GiB":
            return f"{n:.1f} {unidad}"
        n /= 1024
    return f"{n:.1f} GiB"


def descargar_archivo(url: str, destino: Path, tamanio_esperado=None) -> int:
    """Descarga `url` en `destino`. Devuelve la cantidad de bytes escritos."""
    destino.parent.mkdir(parents=True, exist_ok=True)
    temporal = destino.with_name(destino.name + SUFIJO_TEMPORAL)

    ultimo_error = None
    for intento in range(1, INTENTOS + 1):
        try:
            with requests.get(url, stream=True, timeout=TIEMPO_ESPERA, headers=CABECERAS) as respuesta:
                respuesta.raise_for_status()
                escritos = 0
                with temporal.open("wb") as archivo:
                    for bloque in respuesta.iter_content(chunk_size=BLOQUE):
                        if bloque:
                            archivo.write(bloque)
                            escritos += len(bloque)
            if escritos == 0:
                raise requests.RequestException("el servidor devolvio un archivo vacio")
            if tamanio_esperado is not None and escritos != tamanio_esperado:
                raise requests.RequestException(
                    f"tamanio incorrecto: {escritos} B descargados, el servidor anuncia {tamanio_esperado} B"
                )
            temporal.replace(destino)
            return escritos
        except requests.RequestException as error:
            ultimo_error = error
            temporal.unlink(missing_ok=True)
            if intento < INTENTOS:
                print(f"      intento {intento}/{INTENTOS} fallido ({error}); reintentando")

    raise requests.RequestException(f"no se pudo descargar {url}: {ultimo_error}")


def descargar(tipo: str, anio: int, dry_run: bool = False) -> dict:
    """Descarga todos los meses publicados de un tipo de taxi para un anio."""
    print(f"\n=== {tipo.upper()} {anio} ===")
    resumen = {"descargados": 0, "omitidos": 0, "pendientes": 0,
               "no_publicados": [], "fallidos": []}

    for mes in range(1, 13):
        etiqueta = f"{anio}-{mes:02d}"
        destino = ruta_destino(tipo, anio, mes)

        if destino.exists() and destino.stat().st_size > 0:
            print(f"  {etiqueta}  ya existe, se omite")
            resumen["omitidos"] += 1
            continue

        url = construir_url(tipo, anio, mes)
        estado, tamanio = consultar_servidor(url)
        if estado == "no_publicado":
            print(f"  {etiqueta}  aun no publicado por la TLC")
            resumen["no_publicados"].append(etiqueta)
            continue
        if estado == "error":
            print(f"  {etiqueta}  ERROR al consultar el servidor (red?); se reintentara en la proxima ejecucion")
            resumen["fallidos"].append(etiqueta)
            continue

        if dry_run:
            print(f"  {etiqueta}  pendiente de descargar ({formato_tamanio(tamanio or 0)})")
            resumen["pendientes"] += 1
            continue

        print(f"  {etiqueta}  descargando...")
        try:
            escritos = descargar_archivo(url, destino, tamanio)
        except requests.RequestException as error:
            print(f"  {etiqueta}  ERROR: {error}")
            resumen["fallidos"].append(etiqueta)
        else:
            print(f"  {etiqueta}  listo ({formato_tamanio(escritos)}) -> {destino}")
            resumen["descargados"] += 1

    return resumen


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Descarga los datos de taxis (yellow/green) del NYC TLC."
    )
    parser.add_argument(
        "--taxi", choices=(*TIPOS_TAXI, "all"), default="all",
        help="tipo de taxi a descargar (por defecto: all)",
    )
    parser.add_argument(
        "--years", type=int, nargs="+", default=list(ANIOS_POR_DEFECTO), metavar="ANIO",
        help=f"anios a descargar (por defecto: {' '.join(map(str, ANIOS_POR_DEFECTO))})",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="solo informa que se descargaria, sin descargar nada",
    )
    argumentos = parser.parse_args()

    anios = sorted(set(argumentos.years))
    if any(a < 2009 for a in anios):
        parser.error("la TLC publica datos desde 2009")
    tipos = TIPOS_TAXI if argumentos.taxi == "all" else (argumentos.taxi,)

    total = {"descargados": 0, "omitidos": 0, "pendientes": 0, "no_publicados": [], "fallidos": []}
    for anio in anios:
        for tipo in tipos:
            resumen = descargar(tipo, anio, argumentos.dry_run)
            total["descargados"] += resumen["descargados"]
            total["omitidos"] += resumen["omitidos"]
            total["pendientes"] += resumen["pendientes"]
            total["no_publicados"] += [f"{tipo} {m}" for m in resumen["no_publicados"]]
            total["fallidos"] += [f"{tipo} {m}" for m in resumen["fallidos"]]

    print("\n" + "=" * 60)
    print("RESUMEN" + ("  (dry-run)" if argumentos.dry_run else ""))
    print("=" * 60)
    print(f"  anios         : {', '.join(map(str, anios))}")
    print(f"  descargados   : {total['descargados']}")
    print(f"  ya existian   : {total['omitidos']}")
    if argumentos.dry_run:
        print(f"  pendientes    : {total['pendientes']}")
    print(f"  no publicados : {len(total['no_publicados'])}")
    if total["no_publicados"]:
        print(f"      {', '.join(total['no_publicados'])}")
    print(f"  fallidos      : {len(total['fallidos'])}")
    if total["fallidos"]:
        print(f"      {', '.join(total['fallidos'])}")
    print("=" * 60)
    print("Siguiente paso: python scripts/verify_data.py")

    return 1 if total["fallidos"] else 0


if __name__ == "__main__":
    sys.exit(main())
