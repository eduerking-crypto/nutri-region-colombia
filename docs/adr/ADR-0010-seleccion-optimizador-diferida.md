# ADR-0010: Selección del optimizador diferida a un prototipo medible

- **Estado:** Aceptada (Fase 0) — difiere la elección técnica a la Fase 5
- **Fecha:** 2026-10-10

## Contexto

El planificador de menús debe optimizar variedad, adecuación nutricional y costo dentro de límites validados. El prompt maestro menciona OR-Tools como candidato, pero exige que la selección se haga mediante un prototipo medible compatible con las restricciones del proyecto (Python 3.14, sin dependencias pesadas injustificadas, funcionamiento offline posible).

## Decisión

1. No se elige la librería de optimización hoy. La decisión se toma en Fase 5 con un **prototipo medible**: mismo problema de referencia (menú semanal con restricciones reales), comparando al menos dos candidatos (p. ej. OR-Tools vs. PuLP/scipy) en: calidad de solución, tiempo de cómputo, compatibilidad de instalación y mantenimiento.
2. Mientras tanto, la arquitectura aísla la optimización en `backend/app/engine/optimize/` detrás de una interfaz propia, para que el cambio de librería no toque servicios ni UI.
3. El motor puede degradar honestamente: sin solución viable, informa qué restricciones la impiden; nunca relaja requisitos de seguridad para forzar una solución.
4. Resultado del prototipo y elección final → ADR de selección + aprobación del usuario (PD-08).

## Consecuencias

- Ventaja: se evita acoplar el proyecto a una librería que puede no tener ruedas estables para Python 3.14 o resultar desproporcionada.
- Costo: trabajo de interfaz previo; es pequeño y de todos modos necesario para pruebas.
