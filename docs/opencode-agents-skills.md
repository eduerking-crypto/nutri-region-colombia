# Sistema de agentes y skills — OpenCode 1.18.18

Sintaxis verificada el 2026-10-10 contra esta instalación (documentación oficial del esquema + archivos reales de `~/.config/opencode/agents/` y `~/.config/opencode/skills/`). La configuración creada es de **alcance proyecto** (`C:\nutri-region-colombia\.opencode\`) y no modifica nada global.

## Sintaxis verificada

### Agentes — `.opencode/agents/<nombre>.md`

```markdown
---
description: Cuándo usar el agente (visible en el selector).
mode: subagent
---

El cuerpo del archivo ES el prompt del agente.
```

Campos de frontmatter admitidos: `name, model, variant, description, mode, hidden, color, steps, options, permission, disable, temperature, top_p`. No se fijó `model` ni `permission` en ningún agente: heredan el modelo de la sesión y las reglas de permisos existentes (decisión deliberada; puede refinarse más adelante).

### Skills — `.opencode/skills/<nombre>/SKILL.md`

```markdown
---
name: nombre-minusculas-con-guiones
description: Qué hace y cuándo activarla (tercera persona).
---

Cuerpo con instrucciones concretas.
```

`name` obligatorio, en minúsculas con guiones, igual al nombre de la carpeta, ≤ 64 caracteres. `description` obligatoria para que la skill sea visible al modelo.

### Configuración del proyecto

`opencode.json` en la raíz solo declara `"$schema": "https://opencode.ai/config.json"` (config válida mínima, sin alterar comportamiento). `AGENTS.md` se carga automáticamente como instrucciones de todos los agentes.

## Cómo activar

1. Abrir la carpeta `C:\nutri-region-colombia` en OpenCode (o reiniciar OpenCode si ya estaba abierta): la configuración de agentes y skills se carga al inicio, no en caliente.
2. Los agentes aparecen como subagentes invocables; las skills se activan cuando la tarea coincide con su descripción.

## Agentes creados (12)

| Agente | Responsabilidad | Invócalo para |
|---|---|---|
| `orchestrator` | Coordinar fases, distribuir tareas, preparar reportes de fin de fase | planificar y cerrar una fase |
| `software-architect` | Estructura, contratos API, migraciones, ADRs | definir módulos, esquemas, ADR |
| `frontend-specialist` | React/Next.js, componentes, estados, navegación, accesibilidad técnica | construir y revisar UI funcional |
| `ux-ui-designer` | Sistema visual, jerarquía, microinteracciones, usabilidad clínica | dirección visual, prototipos, revisión de flujos |
| `nutrition-data-engineer` | Fuentes, importadores reproducibles, validación de composición | incorporar y auditar datos nutricionales |
| `clinical-evidence-reviewer` | Literatura, limitaciones, reglas CANDIDATAS (nunca las aprueba) | organizar evidencia y proponer reglas |
| `food-biochemistry-researcher` | Nutrientes, bioactivos, transformaciones culinarias, hecho vs. hipótesis | documentar la capa bioquímica |
| `territorial-food-specialist` | Alimentos, mercados, recetas y cultura por regiones de Colombia | estructurar contenido territorial |
| `clinical-rules-engineer` | Implementar reglas aprobadas, conflictos, pruebas de seguridad | codificar y probar el motor determinista |
| `security-privacy-reviewer` | Auth, datos sensibles, vulnerabilidades, checklist Ley 1581 (propone, no certifica) | auditar seguridad y privacidad |
| `qa-test-engineer` | Pruebas unit/integración/regresión/accesibilidad/adversas | diseñar y ejecutar el plan de pruebas |
| `documentation-engineer` | README, diccionario de datos, documentación de API y decisiones | mantener docs al día |

## Skills creadas (12)

| Skill | Propósito |
|---|---|
| `scientific-source-verification` | verificar existencia, versión, licencia y acceso de fuentes; protocolo anti-invención de referencias |
| `nutrition-data-validation` | validar unidades, base 100 g, rangos, duplicados, faltantes; informe de calidad |
| `clinical-rule-safety` | autoría de reglas: versionado, condiciones, excepciones, pruebas y flujo de aprobación |
| `food-biochemistry-evidence` | documentar composición y bioactivos distinguiendo medición, estimación y literatura |
| `regional-food-modeling` | estructurar alimentos, recetas y regionalismo cultural colombiano con verificabilidad |
| `budget-menu-optimization` | costos con procedencia y fecha; nunca garantizar presupuesto sin datos |
| `premium-healthcare-ui` | dirección visual editorial/clínica, animaciones, `prefers-reduced-motion` |
| `accessibility-review` | WCAG 2.2 AA, teclado, contraste, lectores de pantalla |
| `privacy-security-audit` | minimización, secretos, segregación de salud, OWASP, checklist Ley 1581 |
| `test-driven-development` | flujo TDD, nomenclatura, cobertura y casos adversos |
| `api-contract-validation` | contratos OpenAPI, coherencia Pydantic↔TypeScript, cambios rompientes |
| `release-readiness-review` | checklist de cierre de fase y reporte honesto |

## Límites del sistema

- Los agentes comparten las reglas de `AGENTS.md`; ningún agente aprueba sus propios cambios críticos ni declara reglas clínicas aprobadas.
- Los agentes son asistentes de desarrollo: no sustituyen al profesional sanitario ni al revisor legal.
- Configuración no se recarga en caliente: reiniciar OpenCode tras cualquier cambio en `.opencode/` o `opencode.json`.
