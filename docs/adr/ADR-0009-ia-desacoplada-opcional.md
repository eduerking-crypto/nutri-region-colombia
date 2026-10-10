# ADR-0009: IA desacoplada, opcional y sin API de pago obligatoria

- **Estado:** Aceptada (Fase 0)
- **Fecha:** 2026-10-10

## Contexto

El producto contempla una capa de IA para explicar datos verificados, ayudar a buscar literatura y apoyar el desarrollo. Exigencias del responsable: ninguna función fundamental puede depender de una API de pago, la IA no puede alterar resultados del motor determinista (ADR-0004) y debe poder desactivarse sin rombir la app. El entorno verificado tiene Ollama 0.40.1 local.

## Decisión

1. Interfaz de proveedor desacoplada (`AIProvider`): contratos de chat/explicación independientes del proveedor concreto.
2. Candidato por defecto para desarrollo: **Ollama local** (modelos ya presentes en el entorno). Otros proveedores solo como configuración opcional del usuario, nunca como dependencia obligatoria.
3. Casos de uso permitidos de la IA: explicar datos ya verificados, asistencia de búsqueda de literatura (siempre con verificación posterior de referencias), ayuda al equipo de desarrollo. Prohibido: decidir recomendaciones, calcular valores, sustituir reglas, redactar datos científicos finales.
4. Toda salida de IA visible por el usuario se valida contra los datos estructurados antes de mostrarse; afirmaciones no respaldadas por datos verificados se bloquean o marcan como no verificables.
5. Interruptor global: con IA desactivada, todas las funciones nutricionales esenciales operan con normalidad (caso 13 del catálogo adverso).

## Consecuencias

- Ventaja: sin costos recurrentes obligatorios, sin dependencia de conectividad para funciones esenciales, control total sobre lo que la IA puede decir.
- Costo: las explicaciones generadas requieren capa de validación contra datos estructurados (se implementa en Fase 6).
- La elección final del modelo/proveedor por defecto queda en PD-06.
