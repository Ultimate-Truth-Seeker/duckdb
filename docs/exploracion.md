# Ejercicio 3 - Consultas directas sobre archivos Parquet

Consultas: `sql/01_exploracion/p01..p12`. Notebook: `notebooks/01_exploracion.ipynb`.
Resultado, fuente y decision de cada consulta: `docs/consultas_resultados.md` (se genera con `python scripts/document_queries.py --dirs 01_exploracion`).

## Que punto responde cada consulta

| Punto | Consulta |
|---|---|
| 3.1 archivos | `p01_archivos.sql` |
| 3.2 registros | `p02_registros.sql` |
| 3.3 columnas | `p03`, `p04`, `p05`, `p07` |
| 3.4 tipos de datos | `p03`, `p04`, `p05`, `p06` |
| 3.5 muestra | `p08_muestra.sql` |
| 3.6 calidad | `p06`, `p07`, `p09`, `p10`, `p11`, `p12` |
| 3.7 consulta directa | todas leen `read_parquet(...)`, `glob(...)` o `parquet_schema(...)`; ninguna usa una tabla |
| 3.8 documentacion | `docs/consultas_resultados.md` (SQL, objetivo, fuente, resultado, decision) |

Los patrones usan comodin de anio (`data/raw/yellow/*/*.parquet`), de modo que al descargar 2024 y 2025 **no cambia ninguna consulta** (ver `docs/validacion_anios.md`).

## 3.6 Problemas de calidad de datos

Cifras reales sobre los 3 años (121,184,384 viajes: yellow 119,595,677 y green 1,588,707). Fuente: `p09` a `p12`, `v03` y `d02` (ver `docs/consultas_resultados.md`).

| Problema | Se detecta con | Resultado (yellow / green) | Decision |
|---|---|---|---|
| Fechas de recogida fuera del año/mes del archivo | `p11`, `p12`, `v03` | 102 / 55 fuera del año del archivo; 68 / 20 fuera de 2024-2026 (años 2001 a 2009 y 2023); hasta 51 viajes por archivo fuera de su mes | Excluir del análisis temporal con el filtro 2024-2026; no se borran de `trips`. |
| Bajada anterior a la recogida, o duración > 24 h | `p11`, `d02` | 3,820 / 1,351 con bajada antes de recogida; 845 / 6 con más de 24 h | Excluir de duración y velocidad (filtro 1-180 min). |
| Distancia 0 o muy grande (> 100 millas) | `p09`, `p10`, `p11` | Distancia <= 0: 3,131,494 (2.6 %) / 71,224 (4.5 %); > 100 millas: 5,706 / 516; máximo 398,608 millas | Filtrar en indicadores de distancia y velocidad (0.1-100 millas). |
| Tarifa o total negativos o en cero | `p09`, `p11` | Tarifa <= 0: 3,798,269 (3.2 %) / 13,015 (0.8 %); total negativo: 1,744,900 (1.5 %) / 4,971 (0.3 %); tarifa mínima -2,555 y máxima 863,372 | Filtrar `fare_amount` entre 1 y 500 en promedios. |
| `passenger_count` nulo o 0 | `p09`, `p10`, `p11` | 24,172,589 (20.2 %) / 142,558 (9.0 %); 19.58 % de nulos en yellow, junto con `RatecodeID` y `store_and_fwd_flag` | No usar como filtro; reportar el % de nulos. |
| Zonas de recogida fuera de 1-265 | `p11` | 0 / 0 | Sin acción; se mantiene el filtro por seguridad. |
| Columnas que existen solo en un tipo o desde cierto año | `p05`, `p07`, `v04` | `cbd_congestion_fee` desde 2025-01 (20 de 32 archivos por tipo); `request_source` desde 2026-06 (3 archivos); `ehail_fee` 100 % nula en green | Tratarlas como NULL donde no existen (`taxi_common.py`); `request_source` no se incorpora a `trips`. |
| Mismo campo con tipo distinto entre archivos o distinto nombre | `p06`, `p05` | 0 columnas con tipo físico distinto entre archivos; los nombres sí cambian (`tpep_*`/`lpep_*`, `Airport_fee`) | `union_by_name=true`, `TRY_CAST` y mapeo de nombres. |

## 3.9 ¿Que significa consultar directamente un archivo Parquet y por que sirve con volumenes grandes?

Consultar directamente un Parquet es escribir `SELECT ... FROM read_parquet('ruta/*.parquet')` y que DuckDB lea los archivos **en el momento de la consulta**, sin crear una tabla ni copiar los datos antes. Los archivos siguen siendo la unica copia de los datos.

Es util con mucho volumen por cuatro razones:

1. **Formato columnar:** Parquet guarda cada columna por separado; una consulta que usa 3 de 20 columnas lee solo esas 3.
2. **Estadisticas por bloque:** cada archivo guarda minimo y maximo por grupo de filas, y un filtro como `fare_amount > 500` puede saltarse bloques completos. Un `count(*)` puede resolverse casi solo con los metadatos.
3. **Sin carga previa:** no hay que esperar una importacion ni reservar espacio extra; un archivo nuevo en la carpeta ya forma parte de la consulta.
4. **No exige memoria para todo el conjunto:** DuckDB procesa por bloques y en paralelo, y puede ejecutar consultas sobre mas datos que RAM.

El costo es que cada consulta vuelve a abrir los archivos, leer sus metadatos y, si hay que unificar esquemas, convertir tipos; eso se mide en el benchmark del Ejercicio 6 (`docs/benchmark_analisis.md`).
