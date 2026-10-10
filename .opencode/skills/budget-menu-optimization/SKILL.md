---
name: budget-menu-optimization
description: Planificación de menús con presupuesto para NutriRegión Colombia. Úsala al generar menús, listas de compras, costos por porción, alternativas económicas y optimización. Exige procedencia de precios con fecha y prohíbe garantizar presupuesto sin datos.
---

# Budget Menu Optimization

## Objetivo

Proponer menús asequibles y culturalmente pertinentes, con costos honestos: cada cifra sabe de dónde viene y qué tan fresca es.

## Instrucciones

1. Todo costo proviene de registros `observacion_precio` con fecha, tipo de dato (observado/publicado/estimado), fuente y unidad comercial comparable. Prohibido deducir precios por ubicación (ADR-0007).
2. Distingue en cada resultado: costo con precios observados vs. aproximado con referencias — el usuario debe ver cuál es cuál.
3. Sin datos de precio para el municipio: el menú se genera igual, la sección de presupuesto muestra "sin datos" y degrada honestamente. Nunca se inventa un "precio estimado" sin registro.
4. No garantices cumplimiento de presupuesto cuando falten precios, unidades no comparables o información insuficiente: expresa la limitación.
5. La optimización maximiza variedad y adecuación dentro de límites validados, pero JAMÁS relaja seguridad alimentaria ni requisitos nutricionales validados para abaratar.
6. Sin solución viable: informa qué restricciones la impiden; no fuerzas.
7. Lista de compras consolidada: cantidades por porciones, costo total y por porción, alternativas más económicas, aprovechamiento responsable de ingredientes.
8. La librería de optimización se decide por prototipo medible (ADR-0010); el código vive aislado en `engine/optimize/`.

## Criterios de aceptación

- Cada cifra de costo conlleva fecha y tipo de dato visibles en la UI.
- Menús sin datos de precio funcionan y se explican.
- Ningún plan viola alergias/exclusiones para cumplir presupuesto.

## Errores que debe evitar

- "Precio promedio nacional" presentado como precio local.
- Abaratar sacrificando grupos alimentarios esenciales.
- Fingir precisión de centavos con datos estimados.
