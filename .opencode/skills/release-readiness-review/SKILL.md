---
name: release-readiness-review
description: Revisión de preparación y cierre de fase para NutriRegión Colombia. Úsala al terminar cualquier fase o antes de considerar lista una entrega: verifica Definition of Done, reporte honesto de pruebas, riesgos, decisiones pendientes y datos con procedencia.
---

# Release Readiness Review

## Objetivo

Cerrar cada fase con evidencia real y pendientes explícitos — sin inflar el estado del producto.

## Instrucciones

1. Definition of Done (por `docs/test-plan.md`): comprueba punto por punto cada funcionalidad de la fase.
2. Verifica con comandos reales: lint, tipado, pruebas, build. Registra comando + resultado. Si no se ejecutó, el estado es "no verificado", no "OK".
3. Datos: confirma que todo dato publicado tiene procedencia completa y que ningún dato demo se presenta como real (ADR-0005/0006).
4. Reglas clínicas: confirma que ninguna regla `candidate` quedó activa; toda regla activa tiene aprobación registrada (ADR-0004).
5. Accesibilidad y responsive: verifica lo ejecutado y declara lo que falta.
6. Redacta el reporte de cierre de fase con la estructura de `AGENTS.md` §3.2: funcionalidades, archivos, pruebas reales, fuentes y limitaciones, riesgos, decisiones pendientes, plan de la siguiente fase.
7. Actualiza `docs/pending-decisions.md` y los ADRs afectados antes de reportar.
8. Cierra con la pregunta explícita de aprobación y DETENTE.

## Criterios de aceptación

- Cada afirmación del reporte tiene evidencia (comando, archivo, prueba).
- Los pendientes figuran como pendientes — no como "casi listos".
- La fase no se marca completada sin aprobación del usuario.

## Errores que debe evitar

- Reportar funcionalidades inexistentes o no probadas.
- Suavizar fallos de pruebas o datos faltantes.
- Avanzar trabajo de la fase siguiente sin aprobación.
