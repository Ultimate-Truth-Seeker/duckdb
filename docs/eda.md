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

## 4.4 Explicacion de resultados y 4.5 hallazgos relevantes

<!-- COMPLETAR despues de ejecutar sobre los datos reales. Una entrada por hallazgo con: que se observo (cifra), en que consulta, y por que importa. Minimo tres. -->

| # | Hallazgo | Evidencia (consulta y cifra) | Implicacion |
|---|---|---|---|
| 1 | | | |
| 2 | | | |
| 3 | | | |
