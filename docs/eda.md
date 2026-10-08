# Ejercicio 4 - Analisis exploratorio

Notebook: `notebooks/02_eda.ipynb`. Consultas: `sql/02_eda/`. Resultados y decisiones: `docs/consultas_resultados.md`.

## 4.1 Preguntas y justificacion

La justificacion parte de lo que el Ejercicio 3 mostro del conjunto de datos: archivos **mensuales**, dos tipos de taxi con **columnas distintas**, campos de dinero con **valores negativos o extremos** y la propina **solo registrada con tarjeta**.

| # | Pregunta | Por que se plantea | Consulta |
|---|---|---|---|
| P1 | ¿Como evoluciona la demanda mes a mes y hay estacionalidad? | Los datos llegan por mes; un patron mensual condiciona como leer 2024-2026 (y que 2026 esta incompleto). | `d10` |
| P2 | ¿En que dias y horas se concentra la demanda? | Las fechas tienen resolucion de segundos; permite detectar horas pico y diferencias semana/fin de semana. | `d05` |
| P3 | ¿Como es un viaje tipico (distancia, duracion, velocidad) y como se distribuyen estos valores? | Las variables son muy asimetricas; el promedio puede engañar y hay que ver mediana, percentiles y colas. | `d01`, `d03`, `d04` |
| P4 | ¿En que se diferencian los taxis amarillos de los verdes? | Tienen esquema y reglas de operacion distintas; interesa saber si se pueden analizar juntos. | `d11`, `d07` |
| P5 | ¿Como pagan los pasajeros y cuanto dejan de propina? | `payment_type` condiciona si la propina se registra; hay que saber que parte del dato es confiable. | `d06` |
| P6 | ¿Que zonas concentran recogidas y destinos? | Las zonas son la unica variable espacial; se pueden identificar flujos netos. | `d07` |
| P7 | ¿Que variables numericas se relacionan entre si? | Antes de construir indicadores de ingreso conviene saber si la tarifa se explica por la distancia. | `d08` |
| P8 | ¿Que proporcion de registros es atipica o inconsistente? | El Ejercicio 3 mostro tarifas negativas, distancias extremas y fechas fuera de rango. | `d02`, `d09` |

## 4.4 Explicacion de resultados

Cifras sobre los 3 años (121,184,384 viajes); fuente: `docs/consultas_resultados.md`.

| Pregunta | Que muestran los resultados |
|---|---|
| P1 tendencia (`d10`) | Yellow sube de 2024 a 2025 (+13 % a +27 % por mes) y baja de 2025 a 2026 (-3.5 % a -11.2 % de febrero a agosto; enero 2026 +7.2 %). Green baja todos los meses frente al mismo mes del año anterior (-7.0 % a -19.8 %). 2026 solo llega hasta agosto. |
| P2 dia y hora (`d05`) | En yellow la hora pico es las 18 h (8.5 M viajes) y el valle va de 4 a 5 h. El lunes es el dia con menos viajes (14.6 M) y el jueves el de mas (18.6 M). |
| P3 viaje tipico (`d01`, `d03`, `d04`) | Mediana de distancia 1.81 millas en yellow y 1.95 en green; la mediana de duracion es 13.6 y 12.6 min. Alrededor de la mitad de los viajes esta entre 1 y 3 millas (yellow 46 %, green 51 %). Los promedios estan inflados por valores imposibles (distancia maxima 398,608 millas). |
| P4 yellow vs green (`d11`) | Yellow: tarifa media 20.23, distancia 3.49 millas, duracion 17.3 min, 7.2 % de recogidas en las zonas 132 y 138 (las que la consulta trata como JFK y LGA). Green: 17.73, 3.13 millas, 15.7 min y 0 % en esas zonas. Pago con tarjeta: 70.9 % yellow y 68.7 % green. |
| P5 pago y propina (`d06`) | Con tarjeta la propina media es 4.33 (26 % de la tarifa) en yellow; en efectivo es 0.00 porque no se registra. En yellow, `payment_type` 0 son 23,419,814 viajes (19.58 %) y coincide exactamente con los viajes donde `passenger_count` es nulo. |
| P6 zonas (`d07`) | Las zonas 237, 132 y 161 concentran mas recogidas (5.3 M, 5.2 M y 5.2 M). La 132 tiene 5.2 M de recogidas y solo 1.2 M de bajadas (saldo neto +4.0 M). No hay tabla de nombres de zona en el repositorio, por eso se reportan ids. |
| P7 correlaciones (`d08`) | Distancia y tarifa: 0.91 en yellow y 0.74 en green. Los pasajeros casi no se relacionan con el total (0.06 y 0.03). |
| P8 atipicos (`d02`, `d09`) | Yellow: 3.8 M tarifas <= 0 (3.2 %), 3.1 M distancias <= 0 (2.6 %), 845 viajes de mas de 24 h. El criterio IQR marca ~8 % de las tarifas como atipicas altas (limite 45.63 en yellow). |

## 4.5 Hallazgos relevantes

| # | Hallazgo | Evidencia | Implicacion |
|---|---|---|---|
| 1 | Los promedios de distancia y velocidad engañan por valores imposibles. | `d01`: distancia media yellow 5.88 vs mediana 1.81; green 16.99 vs 1.95 (maximo 398,608 millas). `d04`: velocidad media de green 67.7 mph. | Se reporta mediana y se filtra distancia 0.1-100, tarifa 1-500 y duracion 1-180 min en cada consulta. `trips` no se modifica. |
| 2 | La propina solo existe para pagos con tarjeta. | `d06`: tarjeta 67.3 % de los viajes yellow con propina media 4.33; efectivo 10.8 % con 0.00. | Cualquier indicador de propina debe limitarse a `payment_type = 1`. |
| 3 | El 19.58 % de yellow tiene `payment_type` 0 y `passenger_count` nulo a la vez (23.4 M viajes). | Verificado con un conteo cruzado sobre `trips`: 23,419,814 viajes con ambas condiciones y ninguno con solo una. `p09` muestra el mismo porcentaje de nulos en `RatecodeID` y `store_and_fwd_flag`. | No usar `passenger_count` ni `RatecodeID` como filtro; tratar `payment_type` 0 como "sin dato". |
| 4 | El IQR no sirve para limpiar tarifas. | `d09`: 8.16 % de yellow (9.45 M viajes) quedaria como atipico alto. | Son viajes largos legitimos; se usa un filtro fijo de negocio en vez de eliminar por IQR. |
| 5 | La demanda no es estable: cambia de signo entre años y tipos. | `d10`/`v06`: yellow +13 % a +27 % en 2025 y -3.5 % a -11.2 % en 2026; green baja todos los meses. | Comparar siempre el mismo mes entre años; 2026 esta incompleto (hasta agosto). |
| 6 | La zona 132 concentra viajes de salida con poco retorno. | `d07`: 5.2 M recogidas vs 1.2 M bajadas. | Es un flujo neto muy marcado; para nombrarlo con certeza falta la tabla de zonas de la TLC. |
