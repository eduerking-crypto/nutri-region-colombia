---
name: test-driven-development
description: Desarrollo guiado por pruebas para NutriRegión Colombia. Úsala al escribir cualquier funcionalidad de backend o del motor determinista, y en general al implementar lógica de negocio. Define el flujo rojo-verde-refactor, nomenclatura, cobertura por módulo y casos adversos.
---

# Test Driven Development

## Objetivo

Funcionalidades verificables: nada se reporta como terminado sin pruebas escritas, ejecutadas y con resultados reales.

## Instrucciones

1. Flujo por funcionalidad de dominio: escribe primero la prueba que define el comportamiento esperado (incluido el caso adverso) → implementa lo mínimo para pasarla → refactoriza sin romperla.
2. Nomenclatura: `should_<comportamiento>_when_<condición>` (ej. `should_block_plan_when_severe_allergy_confirmed`).
3. Módulo crítico (engine: triage + reglas): cobertura > 90 %, más pruebas de propiedad (hypothesis: mismas entradas → mismas salidas; reglas `candidate` nunca aplican) más el catálogo adverso completo del plan de pruebas. Backend general ≥ 80 %.
4. Junto a cada regla clínica: prueba de disparo correcto + caso negativo (no dispara cuando no debe) + prueba de conflicto.
5. Mocks para dependencias externas en unitarias; integración contra la app real con TestClient; sin bases de datos compartidas entre pruebas.
6. Reporta la evidencia tal cual: comando ejecutado, resumen de resultados, fallos conocidos. Si algo no se pudo probar, se declara.

## Criterios de aceptación

- Las pruebas existen junto con la funcionalidad (mismo cambio, misma fase).
- La cobertura se mide con herramienta, no se estima.
- Los fallos se reportan; nunca se eliminan pruebas para "pasar".

## Errores que debe evitar

- Escribir pruebas después de "terminar" y solo para el camino feliz.
- Cambiar la expectativa de la prueba para que pase.
- Declarar cobertura sin comando de medición ejecutado.
