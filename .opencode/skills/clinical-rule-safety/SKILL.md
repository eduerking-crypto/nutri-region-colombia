---
name: clinical-rule-safety
description: Autoría segura de reglas clínicas para NutriRegión Colombia. Úsala al proponer, versionar, implementar o probar cualquier regla del motor determinista, y al gestionar conflictos entre restricciones. Ninguna regla entra en vigor sin aprobación profesional registrada.
---

# Clinical Rule Safety

## Objetivo

Que el motor determinista solo ejecute criterios clínicos aprobados, versionados, probados y trazables.

## Instrucciones

1. Toda regla vive como dato versionado en `data/rules/` con: id (`CR-<ambito>-<número>`), versión, ámbito, condiciones, excepciones, acción (`bloquear_plan` / `requerir_revision_profesional` / `advertir` / `derivar_urgencia`), justificación y fuente aplicable.
2. Toda regla nueva nace `status: candidate`. El motor SOLO ejecuta `approved`.
3. Aprobación: solo un profesional sanitario competente puede pasar una regla a `approved`; se registran `reviewer`, `approved_at` y `next_review` (PD-02). Sin eso, la regla no existe para el motor.
4. Pruebas ANTES de activar: casos adversos del plan de pruebas que apliquen a esa regla + caso negativo (la regla NO dispara cuando no debe) + prueba de propiedad de reproducibilidad.
5. Conflictos entre restricciones: nunca se fuerza una solución. Se explica el conflicto y se deriva según la acción de mayor severidad.
6. Alergia grave confirmada: ninguna sustitución se presenta como segura sin información de ingredientes, contaminación cruzada y preparación.
7. Señales de urgencia: la derivación a atención profesional se muestra antes que cualquier contenido de plan.
8. Cambios de reglas (crear, editar, aprobar, retirar) quedan en auditoría.

## Fuentes permitidas para umbrales

Solo fuentes verificadas y aplicables a población colombiana cuando existan (guías nacionales, recomendaciones OMS/OPS citadas con versión). Prohibido derivar umbrales de "sentido común".

## Errores que debe evitar

- Inventar o aproximar umbrales clínicos.
- Activar reglas candidatas "provisionalmente".
- Dejar que la IA generativa modifique condiciones o acciones de reglas.
- Presentar advertencias como diagnóstico o viceversa.
