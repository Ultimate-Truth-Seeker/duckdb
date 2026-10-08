#!/usr/bin/env python3
"""Configura Metabase para el tablero del Ejercicio 7 usando su API.

Hace, de forma idempotente (se puede repetir sin duplicar nada):
  1. crea la cuenta de administrador local si Metabase aun no esta configurado;
  2. registra la conexion a taxi.duckdb en SOLO LECTURA;
  3. crea una pregunta (tarjeta) nativa por cada sql/05_indicadores/i*.sql;
  4. arma el dashboard "Lab 8 - Taxis NYC" con todas las tarjetas.

Las credenciales NO van en el repositorio: se leen de variables de entorno.
    MB_ADMIN_EMAIL       correo de la cuenta local (obligatoria)
    MB_ADMIN_PASSWORD    contrasena de la cuenta local (obligatoria)
    MB_URL               por defecto http://metabase:3000 (dentro de la red de docker compose)
    MB_DB_FILE           por defecto /workspace/data/processed/taxi.duckdb (ruta DENTRO del contenedor de Metabase)
    MB_DUCKDB_MEMORY     tope de memoria de duckdb dentro de Metabase, por defecto 3GB

Uso (el contenedor lab ve a Metabase por su nombre de servicio):
    docker compose exec -e MB_ADMIN_EMAIL=... -e MB_ADMIN_PASSWORD=... lab python scripts/metabase_setup.py
"""

import os
import sys
import time
from pathlib import Path

import requests

import taxi_common as tc

URL = os.environ.get("MB_URL", "http://metabase:3000").rstrip("/")
DB_FILE = os.environ.get("MB_DB_FILE", "/workspace/data/processed/taxi.duckdb")
MEMORIA_DUCKDB = os.environ.get("MB_DUCKDB_MEMORY", "3GB")
NOMBRE_DB = "taxi"
NOMBRE_COLECCION = "Lab 8 - Taxis NYC"
NOMBRE_DASHBOARD = "Lab 8 - Taxis NYC"
ESPERA = 60   # segundos por peticion

# titulo, visualizacion y configuracion de cada indicador (clave = nombre del .sql sin extension)
INDICADORES = {
    "i01_viajes_por_mes_y_tipo": {
        "titulo": "I1 Viajes por mes y tipo de taxi", "display": "line",
        "settings": {"graph.dimensions": ["mes", "taxi_type"], "graph.metrics": ["viajes"],
                     "series_settings": {"green": {"axis": "right"}}},
        "pos": (0, 0, 12, 7)},
    "i02_ingresos_por_mes_y_tipo": {
        "titulo": "I2 Ingresos por mes (millones de USD)", "display": "bar",
        "settings": {"graph.dimensions": ["mes", "taxi_type"], "graph.metrics": ["ingresos_millones"],
                     "stackable.stack_type": "stacked"},
        "pos": (0, 12, 12, 7)},
    "i03_demanda_por_dia_y_hora": {
        "titulo": "I3 Demanda por hora y dia de la semana", "display": "line",
        "settings": {"graph.dimensions": ["hora", "nombre_dia"], "graph.metrics": ["viajes"]},
        "pos": (7, 0, 12, 7)},
    "i04_pago_y_propina": {
        "titulo": "I4 Forma de pago (% de viajes)", "display": "bar",
        "settings": {"graph.dimensions": ["tipo_pago", "taxi_type"], "graph.metrics": ["pct_viajes"]},
        "pos": (7, 12, 12, 7)},
    "i05_top_zonas_recogida": {
        "titulo": "I5 Top 10 zonas de recogida (id de zona)", "display": "row",
        "settings": {"graph.dimensions": ["zona"], "graph.metrics": ["viajes"]},
        "pos": (14, 0, 8, 8)},
    "i06_viaje_tipico_por_anio": {
        "titulo": "I6 Viaje tipico por anio (medianas)", "display": "table",
        "settings": {"column_settings": {
            '["name","taxi_type"]': {"column_title": "Tipo"},
            '["name","anio"]': {"column_title": "Año", "number_separators": "."},
            '["name","viajes"]': {"column_title": "Viajes"},
            '["name","distancia_mediana_millas"]': {"column_title": "Dist. mediana (mi)"},
            '["name","duracion_mediana_min"]': {"column_title": "Duración mediana (min)"},
            '["name","tarifa_mediana"]': {"column_title": "Tarifa mediana"}}},
        "pos": (14, 8, 16, 8)},
    "i07_variacion_interanual": {
        "titulo": "I7 Variacion interanual del mismo mes (%)", "display": "bar",
        "settings": {"graph.dimensions": ["mes", "taxi_type"], "graph.metrics": ["variacion_pct"]},
        "pos": (22, 0, 12, 7)},
    "i08_calidad_por_anio_y_tipo": {
        "titulo": "I8 Registros inconsistentes por anio (%)", "display": "bar",
        "settings": {"graph.dimensions": ["anio", "taxi_type"], "graph.metrics": ["pct_alguna"],
                     "column_settings": {'["name","anio"]': {"number_separators": "."}}},
        "pos": (22, 12, 12, 7)},
}


def salir(mensaje):
    print(f"ERROR: {mensaje}", file=sys.stderr)
    sys.exit(1)


def credenciales():
    email, clave = os.environ.get("MB_ADMIN_EMAIL"), os.environ.get("MB_ADMIN_PASSWORD")
    if not email or not clave:
        salir("faltan MB_ADMIN_EMAIL y MB_ADMIN_PASSWORD (variables de entorno)")
    return email, clave


def llamar(sesion, metodo, ruta, **kw):
    r = sesion.request(metodo, f"{URL}{ruta}", timeout=ESPERA, **kw)
    if not r.ok:
        # no se imprime el cuerpo de la peticion (puede llevar la contrasena), solo la respuesta
        salir(f"{metodo} {ruta} -> {r.status_code}: {r.text[:400]}")
    return r.json() if r.content else None


def esperar_metabase(sesion):
    for _ in range(60):
        try:
            if sesion.get(f"{URL}/api/health", timeout=5).ok:
                return
        except requests.RequestException:
            pass
        time.sleep(2)
    salir(f"Metabase no responde en {URL}")


def iniciar_sesion(sesion, email, clave):
    props = llamar(sesion, "GET", "/api/session/properties")
    if not props.get("has-user-setup"):
        print("configurando Metabase por primera vez (cuenta de administrador local)")
        llamar(sesion, "POST", "/api/setup", json={
            "token": props["setup-token"],
            "user": {"first_name": "Lab8", "last_name": "Admin", "email": email, "password": clave},
            "prefs": {"site_name": "Lab 8 DuckDB", "site_locale": "es", "allow_tracking": False},
        })
    sid = llamar(sesion, "POST", "/api/session", json={"username": email, "password": clave})["id"]
    sesion.headers["X-Metabase-Session"] = sid


def asegurar_base(sesion):
    # solo lectura y con tope de memoria: duckdb corre dentro de la jvm de metabase y sin tope puede tumbar el contenedor
    detalles = {"database_file": DB_FILE, "read_only": True, "memory_limit": MEMORIA_DUCKDB}
    for db in llamar(sesion, "GET", "/api/database")["data"]:
        if db["name"] == NOMBRE_DB:
            if any(db["details"].get(k) != v for k, v in detalles.items()):
                # duckdb no deja reabrir el archivo con otra configuracion si ya hay conexiones abiertas
                r = sesion.put(f"{URL}/api/database/{db['id']}", json={"details": detalles}, timeout=ESPERA)
                if r.ok:
                    print(f"base '{NOMBRE_DB}' ya existe (id {db['id']}), conexion actualizada")
                else:
                    print(f"AVISO: no se pudo actualizar la conexion ({r.status_code}); reinicie Metabase "
                          "(docker compose restart metabase) y vuelva a ejecutar este script")
            else:
                print(f"base '{NOMBRE_DB}' ya existe (id {db['id']}), sin cambios")
            return db["id"]
    db = llamar(sesion, "POST", "/api/database", json={
        "name": NOMBRE_DB, "engine": "duckdb", "details": detalles,
        "is_full_sync": True, "auto_run_queries": False})
    print(f"base '{NOMBRE_DB}' creada (id {db['id']}), solo lectura sobre {DB_FILE}")
    return db["id"]


def asegurar_coleccion(sesion):
    for c in llamar(sesion, "GET", "/api/collection"):
        if c.get("name") == NOMBRE_COLECCION and not c.get("archived"):
            return c["id"]
    return llamar(sesion, "POST", "/api/collection", json={"name": NOMBRE_COLECCION})["id"]


def leer_sql(clave):
    texto = (tc.REPO_ROOT / "sql" / "05_indicadores" / f"{clave}.sql").read_text(encoding="utf-8")
    return texto.strip().rstrip(";")   # metabase no admite el ; final en consultas nativas


def asegurar_tarjetas(sesion, db_id, coleccion_id):
    existentes = {c["name"]: c for c in llamar(sesion, "GET", "/api/card") if c.get("collection_id") == coleccion_id}
    ids = {}
    for clave, spec in INDICADORES.items():
        cuerpo = {
            "name": spec["titulo"], "display": spec["display"],
            "visualization_settings": spec["settings"], "collection_id": coleccion_id,
            "dataset_query": {"type": "native", "database": db_id,
                              "native": {"query": leer_sql(clave), "template-tags": {}}},
        }
        if spec["titulo"] in existentes:
            ids[clave] = existentes[spec["titulo"]]["id"]
            llamar(sesion, "PUT", f"/api/card/{ids[clave]}", json=cuerpo)
            print(f"tarjeta actualizada: {spec['titulo']}")
        else:
            ids[clave] = llamar(sesion, "POST", "/api/card", json=cuerpo)["id"]
            print(f"tarjeta creada: {spec['titulo']}")
    return ids


def asegurar_dashboard(sesion, coleccion_id, ids_tarjetas):
    dash = next((d for d in llamar(sesion, "GET", f"/api/collection/{coleccion_id}/items")["data"]
                 if d["model"] == "dashboard" and d["name"] == NOMBRE_DASHBOARD), None)
    if dash:
        dash_id = dash["id"]
    else:
        dash_id = llamar(sesion, "POST", "/api/dashboard", json={
            "name": NOMBRE_DASHBOARD, "collection_id": coleccion_id,
            "description": "Indicadores del Lab 8 (sql/05_indicadores) sobre taxi.duckdb, 2024-2026."})["id"]
    dashcards = [
        {"id": -(i + 1), "card_id": ids_tarjetas[clave], "row": spec["pos"][0], "col": spec["pos"][1],
         "size_x": spec["pos"][2], "size_y": spec["pos"][3]}
        for i, (clave, spec) in enumerate(INDICADORES.items())
    ]
    llamar(sesion, "PUT", f"/api/dashboard/{dash_id}", json={"dashcards": dashcards})
    print(f"dashboard listo: {URL}/dashboard/{dash_id}")
    return dash_id


def main() -> int:
    email, clave = credenciales()
    sesion = requests.Session()
    esperar_metabase(sesion)
    iniciar_sesion(sesion, email, clave)
    db_id = asegurar_base(sesion)
    coleccion_id = asegurar_coleccion(sesion)
    ids = asegurar_tarjetas(sesion, db_id, coleccion_id)
    asegurar_dashboard(sesion, coleccion_id, ids)
    return 0


if __name__ == "__main__":
    sys.exit(main())
