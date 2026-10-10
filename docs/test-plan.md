# Plan de pruebas — NutriRegión Colombia

Estado: plan de Fase 0. Las herramientas se instalarán en sus fases correspondientes y con autorización explícita (nada se instala ahora). Preregistro honesto: **las pruebas de software no sustituyen la validación nutricional, médica, legal ni de privacidad.**

## Estrategia por tipo

| Tipo | Herramienta prevista | Fase de introducción |
|---|---|---|
| Unitarias backend | pytest (+ hypothesis para pruebas de propiedad) | Fase 2 |
| Integración API | pytest + FastAPI TestClient | Fase 2 |
| Calidad de datos | pytest sobre validadores de importación (rangos, unidades, duplicados, faltantes) | Fase 2 |
| Reglas clínicas | pytest unit + propiedad + adversarial (motor aislado) | Fase 3 |
| Contract / OpenAPI | esquema autogenerado + verificación de tipos en frontend | Fase 1/2 |
| Unitarias frontend | Vitest + React Testing Library | Fase 1 |
| E2E | Playwright | Fase 1 |
| Accesibilidad | axe + revisión manual (teclado, lector de pantalla) | Fase 1 |
| Seguridad | pip-audit / npm audit + revisión OWASP + casos adversos | Fase 3+ |
| Rendimiento | Lighthouse / métricas de carga en pantallas clave | Fase 8 |

## Objetivos de cobertura

- **Módulo de reglas clínicas y triage: > 90 %** de cobertura, complementado con pruebas de propiedad (hypothesis) y el catálogo adverso completo de abajo.
- Backend general: ≥ 80 %.
- Flujos esenciales de UI: pruebas E2E para registro, onboarding, explorador, ficha y planificador.
- La cobertura por sí sola no demuestra seguridad: cada regla exige también pruebas adversas documentadas.

## Catálogo adverso (módulo de triage, Fase 3)

Cada caso debe tener prueba automatizada y resultado esperado explícito:

1. Alergia grave confirmada → alimento excluido; sustitución solo con información suficiente de ingredientes/contaminación cruzada; si no la hay → advertencia explícita, no silencio.
2. Restricciones incompatibles entre sí (ej. alergia + condición que exige el mismo grupo) → no forzar solución; explicar conflicto; derivar a revisión profesional.
3. Perfil incompleto → el motor no genera recomendación individualizada; solicita lo estrictamente necesario y explica por qué.
4. Datos faltantes de precio/disponibilidad → el plan se genera sin garantía de presupuesto, con aviso expreso.
5. Condición renal avanzada autorreportada → bloqueo de plan automático + derivación profesional.
6. Diabetes con medicamentos hipoglucemiantes → derivación profesional; el plan automático no se genera.
7. Embarazo de riesgo / lactancia especial → derivación profesional.
8. Señales de posible trastorno de conducta alimentaria → mensaje de cuidado, sin plan, con derivación.
9. Desnutrición / pérdida involuntaria de peso → derivación profesional.
10. Interacción alimento-medicamento relevante documentada → advertencia con fuente; nunca oculta.
11. Síntomas de alarma → orientación de atención urgente ANTES que cualquier plan.
12. Regla `candidate` (no aprobada) → nunca se aplica, aunque exista en el catálogo.
13. IA desactivada → todas las funciones nutricionales esenciales siguen operando.
14. Un usuario no puede leer datos de otro usuario (prueba de aislamiento multiusuario).

## Definition of Done (por funcionalidad)

1. Pruebas escritas y **ejecutadas** con resultados reales reportados.
2. Lint y tipado estático limpios (ruff/mypy; eslint/tsc) cuando exista código.
3. Estados de UI implementados: carga, vacío, error, éxito, sin datos (Fase 1+).
4. Accesibilidad verificada en lo aplicable (contraste, teclado, `prefers-reduced-motion`).
5. Datos usados con procedencia completa o marcados explícitamente como DEMO.
6. Documentación actualizada si cambia contrato, esquema o decisión.

## Criterios de aceptación por fase (resumen operativo)

Los criterios completos están en el prompt maestro del proyecto (sección 16). Verificación mínima al cerrar cada fase:

- Cada dato publicado tiene procedencia identificable.
- Cálculos reproducibles con unidades coherentes.
- Alergias y restricciones probadas con casos adversos.
- La app comunica explícitamente la incertidumbre y los datos faltantes.
- Los flujos esenciales funcionan en móvil, tablet y escritorio.
- Ninguna función se declara terminada sin pruebas y evidencia del resultado.
- Problemas conocidos y criterios pendientes de aprobación documentados.
