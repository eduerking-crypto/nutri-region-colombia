# ADR-0005: Capas de confianza y procedencia obligatoria en todos los datos

- **Estado:** Aceptada (Fase 0) — decisión estratégica del responsable
- **Fecha:** 2026-10-10

## Contexto

Decisión estratégica del proyecto: **la confianza científica debe ser parte de la interfaz**. Los usuarios deben distinguir sin ambigüedad entre lo que se midió, lo que se estimó, lo que la literatura describe y lo que es explicación educativa. Mezclar estas capas es la forma más rápida de perder credibilidad y de inducir errores de interpretación.

## Decisión

1. Cuatro capas de confianza obligatorias en todo dato y texto científico:
   - `medido` — valor analítico o de tabla oficial identificable
   - `estimado` — cálculo/imputación, siempre con método declarado
   - `literatura` — propiedad descrita en literatura revisada por pares, con referencia concreta
   - `educativo` — explicación didáctica, sin pretensión de dato
2. Procedencia mínima no negociable para publicar un dato: fuente (`source_id`), versión, fecha de consulta (`retrieved_at`) y estado de verificación.
3. La UI muestra la capa de confianza visiblemente en cada ficha, precio, afirmación de evidencia y explicación. Un dato sin procedencia completa no se publica.
4. La ausencia de datos se muestra como tal ("sin datos"), nunca se rellena con supuestos.

## Consecuencias

- Ventaja: separa composición (dato) de beneficio (interpretación) — refuerza el principio "dato ≠ interpretación" y protege frente a afirmaciones terapéuticas no demostradas.
- Costo: más campos por registro y más trabajo de importación; se amortiza porque los importadores validan procedencia desde la Fase 2 (skill `nutrition-data-validation`).
- Requisito de pruebas: los casos del plan de pruebas incluyen "dato faltante → estado visible" y "dato estimado → método visible".
