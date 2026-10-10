# ADR-0004: Motor determinista de recomendaciones, separado de la IA

- **Estado:** Aceptada (Fase 0) — principio de seguridad del producto
- **Fecha:** 2026-10-10

## Contexto

El producto genera recomendaciones que pueden afectar la salud. Un modelo generativo no es auditable, no garantiza el mismo resultado ante la misma entrada y puede inventar o contradecir reglas de seguridad. Las funciones críticas exigen reproducibilidad, auditabilidad y control de versiones.

## Decisión

1. Todo cálculo, control de seguridad y recomendación la produce un **motor determinista de reglas versionadas**: mismas entradas → mismas salidas, con registro de qué reglas (id + versión) se aplicaron a cada resultado.
2. Las reglas se definen como **datos versionados** (`data/rules/`), no como código hardcodeado en la UI ni en prompts.
3. El motor solo ejecuta reglas con `status: approved` (aprobación de profesional competente registrada). Las reglas `candidate` existen documentadas pero jamás se aplican.
4. La IA generativa queda fuera de la ruta de decisión: solo puede explicar datos ya verificados y sus salidas se validan contra los datos estructurados; puede desactivarse sin romper funciones esenciales (complementa ADR-0009).

## Consecuencias

- Ventaja: auditabilidad total ("¿por qué me recomienda esto?" → reglas aplicadas + fuentes), reproducibilidad y pruebas adversas posibles (catálogo del plan de pruebas).
- Costo: las reglas requieren mantenimiento versionado y flujo de aprobación (PD-02, PD-11).
- Impedimento explícito: ninguna fase puede "simplificar" esto delegando decisiones de seguridad a un modelo generativo, aunque acelere el desarrollo.
