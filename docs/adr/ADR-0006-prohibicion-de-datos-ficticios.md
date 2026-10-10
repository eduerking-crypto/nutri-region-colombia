# ADR-0006: Prohibición de datos ficticios presentados como reales

- **Estado:** Aceptada (Fase 0) — principio de integridad del producto
- **Fecha:** 2026-10-10

## Contexto

La presión de "hacer que la app parezca terminada" empuja a inventar catálogos, precios, recetas y hasta referencias científicas. En un producto de salud, un dato inventado no es un placeholder: es una mentira con consecuencias potenciales. El responsable ha fijado como regla dura: no se inventa un catálogo para aparentar completitud.

## Decisión

1. Prohibido crear valores de composición nutricional, precios, disponibilidad, referencias (DOI/PMID) o reglas clínicas que no provengan de una fuente verificable.
2. Es preferible comenzar con un conjunto pequeño, trazable y real antes que cientos de registros incompletos o apócrifos.
3. Los datos demostrativos que la UI necesite antes de la Fase 2 (prototipo visual) se marcan visualmente como **DEMO**, se almacenan separados de los datos reales y se eliminan al incorporar datos verificados.
4. `data/` permanece vacío hasta que exista una fuente con licencia verificada (PD-04) e importador reproducible (Fase 2).
5. Los estados "sin datos", "dato estimado" y "sin verificar" son ciudadanos de primera clase en la interfaz.

## Consecuencias

- Ventaja: la credibilidad del catálogo es total desde el primer registro publicado.
- Costo: la Fase 1 (visual) debe diseñar estados vacíos con esmero, porque el prototipo navegable no tendrá datos reales que mostrar.
- Verificación: cualquier revisión de fase debe comprobar que ningún dato sin procedencia llegó a producción.
