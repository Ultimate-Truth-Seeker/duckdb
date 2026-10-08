# Resultados del benchmark: Parquet directo vs tabla DuckDB

Generado por `scripts/benchmark.py`. Tiempos en segundos (mediana de las ejecuciones; entre parentesis, la primera ejecucion).

Entorno: duckdb=1.5.5, cpus=16, threads=por defecto, memory_limit=por defecto, runs=5, build_seconds=146.1, db_gb=3.28

| Meses | Archivos | GiB Parquet | Filas | Consulta | Parquet (s) | Tabla (s) | Parquet / Tabla | Resultados iguales |
|---:|---:|---:|---:|---|---:|---:|---:|:-:|
| 1 | 2 | 0.048 | 3,021,175 | q01_conteo_total | 0.044 (0.053) | 0.191 (0.421) | 0.23x | si |
| 1 | 2 | 0.048 | 3,021,175 | q02_viajes_por_mes_y_tipo | 0.240 (0.404) | 0.253 (3.301) | 0.95x | si |
| 1 | 2 | 0.048 | 3,021,175 | q03_tarifas_por_tipo_pago | 0.218 (0.260) | 0.303 (4.572) | 0.72x | si |
| 1 | 2 | 0.048 | 3,021,175 | q04_top_zonas_recogida | 0.107 (0.215) | 0.259 (2.630) | 0.41x | si |
| 1 | 2 | 0.048 | 3,021,175 | q05_perfil_dia_hora | 0.227 (0.224) | 0.241 (0.247) | 0.94x | si |
| 1 | 2 | 0.048 | 3,021,175 | q06_filtro_selectivo_atipicos | 0.175 (0.151) | 0.278 (0.278) | 0.63x | si |
| 1 | 2 | 0.048 | 3,021,175 | q07_escaneo_multiples_columnas | 0.243 (0.256) | 0.418 (4.238) | 0.58x | si |
| 1 | 2 | 0.048 | 3,021,175 | q08_mediana_y_percentil | 0.828 (0.828) | 0.779 (0.848) | 1.06x | si |
| 3 | 6 | 0.153 | 9,722,363 | q01_conteo_total | 0.076 (0.137) | 0.134 (0.390) | 0.57x | si |
| 3 | 6 | 0.153 | 9,722,363 | q02_viajes_por_mes_y_tipo | 0.360 (0.562) | 0.263 (2.670) | 1.37x | si |
| 3 | 6 | 0.153 | 9,722,363 | q03_tarifas_por_tipo_pago | 0.307 (0.445) | 0.285 (3.293) | 1.08x | si |
| 3 | 6 | 0.153 | 9,722,363 | q04_top_zonas_recogida | 0.160 (0.223) | 0.172 (2.484) | 0.93x | si |
| 3 | 6 | 0.153 | 9,722,363 | q05_perfil_dia_hora | 0.344 (0.333) | 0.202 (0.202) | 1.70x | si |
| 3 | 6 | 0.153 | 9,722,363 | q06_filtro_selectivo_atipicos | 0.265 (0.304) | 0.277 (0.283) | 0.96x | si |
| 3 | 6 | 0.153 | 9,722,363 | q07_escaneo_multiples_columnas | 0.389 (0.389) | 0.388 (3.432) | 1.00x | si |
| 3 | 6 | 0.153 | 9,722,363 | q08_mediana_y_percentil | 1.504 (1.579) | 1.621 (1.730) | 0.93x | si |
| 6 | 12 | 0.326 | 20,671,900 | q01_conteo_total | 0.132 (0.155) | 0.151 (0.712) | 0.87x | si |
| 6 | 12 | 0.326 | 20,671,900 | q02_viajes_por_mes_y_tipo | 0.623 (0.966) | 0.352 (2.618) | 1.77x | si |
| 6 | 12 | 0.326 | 20,671,900 | q03_tarifas_por_tipo_pago | 0.588 (0.716) | 0.340 (3.619) | 1.73x | si |
| 6 | 12 | 0.326 | 20,671,900 | q04_top_zonas_recogida | 0.293 (0.487) | 0.199 (2.730) | 1.47x | si |
| 6 | 12 | 0.326 | 20,671,900 | q05_perfil_dia_hora | 0.715 (0.720) | 0.235 (0.280) | 3.04x | si |
| 6 | 12 | 0.326 | 20,671,900 | q06_filtro_selectivo_atipicos | 0.517 (0.515) | 0.299 (0.352) | 1.73x | si |
| 6 | 12 | 0.326 | 20,671,900 | q07_escaneo_multiples_columnas | 0.801 (0.861) | 0.449 (2.356) | 1.78x | si |
| 6 | 12 | 0.326 | 20,671,900 | q08_mediana_y_percentil | 2.800 (2.742) | 3.297 (3.297) | 0.85x | si |
| 12 | 24 | 0.66 | 41,829,938 | q01_conteo_total | 0.243 (0.242) | 0.162 (0.451) | 1.51x | si |
| 12 | 24 | 0.66 | 41,829,938 | q02_viajes_por_mes_y_tipo | 1.202 (1.559) | 0.539 (3.611) | 2.23x | si |
| 12 | 24 | 0.66 | 41,829,938 | q03_tarifas_por_tipo_pago | 1.131 (1.288) | 0.427 (4.301) | 2.65x | si |
| 12 | 24 | 0.66 | 41,829,938 | q04_top_zonas_recogida | 0.633 (0.771) | 0.228 (3.096) | 2.78x | si |
| 12 | 24 | 0.66 | 41,829,938 | q05_perfil_dia_hora | 1.378 (1.378) | 0.341 (0.336) | 4.05x | si |
| 12 | 24 | 0.66 | 41,829,938 | q06_filtro_selectivo_atipicos | 1.039 (1.058) | 0.404 (0.404) | 2.57x | si |
| 12 | 24 | 0.66 | 41,829,938 | q07_escaneo_multiples_columnas | 1.532 (1.532) | 0.689 (3.712) | 2.22x | si |
| 12 | 24 | 0.66 | 41,829,938 | q08_mediana_y_percentil | 6.265 (6.418) | 5.361 (7.258) | 1.17x | si |
| 24 | 48 | 1.447 | 91,143,915 | q01_conteo_total | 0.907 (1.871) | 0.265 (0.569) | 3.42x | si |
| 24 | 48 | 1.447 | 91,143,915 | q02_viajes_por_mes_y_tipo | 2.777 (7.231) | 1.098 (3.575) | 2.53x | si |
| 24 | 48 | 1.447 | 91,143,915 | q03_tarifas_por_tipo_pago | 2.167 (2.567) | 0.661 (7.291) | 3.28x | si |
| 24 | 48 | 1.447 | 91,143,915 | q04_top_zonas_recogida | 1.300 (1.509) | 0.355 (4.095) | 3.67x | si |
| 24 | 48 | 1.447 | 91,143,915 | q05_perfil_dia_hora | 2.638 (2.652) | 0.588 (0.654) | 4.49x | si |
| 24 | 48 | 1.447 | 91,143,915 | q06_filtro_selectivo_atipicos | 2.161 (2.078) | 0.648 (0.648) | 3.34x | si |
| 24 | 48 | 1.447 | 91,143,915 | q07_escaneo_multiples_columnas | 3.038 (3.038) | 0.876 (4.171) | 3.47x | si |
| 24 | 48 | 1.447 | 91,143,915 | q08_mediana_y_percentil | 15.058 (14.595) | 13.840 (15.396) | 1.09x | si |
| 32 | 64 | 1.931 | 121,184,384 | q01_conteo_total | 0.762 (0.780) | 0.002 (0.051) | 476.50x | si |
| 32 | 64 | 1.931 | 121,184,384 | q02_viajes_por_mes_y_tipo | 3.151 (4.321) | 1.052 (4.696) | 2.99x | si |
| 32 | 64 | 1.931 | 121,184,384 | q03_tarifas_por_tipo_pago | 2.758 (3.958) | 0.554 (5.621) | 4.98x | si |
| 32 | 64 | 1.931 | 121,184,384 | q04_top_zonas_recogida | 1.681 (1.996) | 0.123 (3.475) | 13.66x | si |
| 32 | 64 | 1.931 | 121,184,384 | q05_perfil_dia_hora | 3.447 (3.360) | 0.451 (0.437) | 7.64x | si |
| 32 | 64 | 1.931 | 121,184,384 | q06_filtro_selectivo_atipicos | 2.634 (2.584) | 0.454 (0.434) | 5.81x | si |
| 32 | 64 | 1.931 | 121,184,384 | q07_escaneo_multiples_columnas | 4.206 (4.402) | 0.748 (3.816) | 5.62x | si |
| 32 | 64 | 1.931 | 121,184,384 | q08_mediana_y_percentil | 19.357 (19.357) | 20.298 (21.653) | 0.95x | si |

Tiempo de construccion de la tabla materializada: 146.1 s; tamanio del archivo .duckdb: 3.28 GiB.

`Parquet / Tabla` > 1 significa que la tabla materializada fue mas rapida.
