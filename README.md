# NutriRegión Colombia

Plataforma digital de nutrición territorial: recomendaciones alimentarias contextualizadas en el territorio, el presupuesto, la cultura gastronómica y las necesidades individuales de las personas en Colombia, con rigor científico trazable.

> **Estado: Fase 0 — Descubrimiento y arquitectura. Completada, pendiente de aprobación.**
> Este repositorio contiene por diseño solo documentación y configuración de agentes/skills. No hay producto funcional, no hay dependencias instaladas y no hay datos publicados todavía.

## Qué es (y qué no es)

NutriRegión Colombia responde preguntas reales:

- ¿Qué puedo comer de forma saludable con el dinero que tengo esta semana?
- ¿Qué alimentos son habituales y están disponibles en mi municipio?
- ¿Cómo preparo platos tradicionales de mi región con mejores características nutricionales?
- ¿Qué contiene cada alimento, con qué evidencia y por qué se me recomienda?

**No es** una calculadora de calorías, ni un chatbot nutricional, ni un generador genérico de dietas.

## Principios no negociables

1. **Rigor científico** — no se inventan datos nutricionales, referencias, precios ni recomendaciones clínicas.
2. **Trazabilidad** — cada dato científico tiene fuente, unidades, fecha y nivel de confianza identificables.
3. **Datos ≠ interpretación** — una composición nutricional no demuestra automáticamente un beneficio clínico.
4. **Seguridad primero** — ninguna recomendación pasa por encima de una alergia, contraindicación o regla clínica validada.
5. **IA controlada** — los modelos generativos explican datos verificados; nunca sustituyen las reglas deterministas de seguridad.
6. **Transparencia** — la incertidumbre, los datos faltantes y la evidencia contradictoria se muestran expresamente.
7. **Pertinencia territorial y accesibilidad económica** — se respeta la gastronomía regional y el presupuesto real de las personas.
8. **Privacidad y no estigmatización** — mínimos datos necesarios, máximo respeto por peso, ingresos y cultura.
9. **Validación profesional** — las reglas clínicas requieren revisión de profesionales competentes antes de habilitarse.
10. **Desarrollo verificable** — nada se declara terminado si no existe, no funciona o no ha sido probado.

## Tres compromisos estratégicos

1. **La OMS y la OPS son referencia, no certificación.** El producto se diseña alineado con sus recomendaciones; cualquier colaboración, reconocimiento o adopción institucional requerirá un proceso independiente. Ver `docs/adr/ADR-0008`.
2. **La plataforma no finge conocer precios.** Cada precio muestra fecha, tipo de dato (observado / publicado / estimado), fuente y nivel de confianza. Sin datos, se dice expresamente y la aplicación sigue siendo útil. Ver `docs/adr/ADR-0007`.
3. **La confianza científica es parte de la interfaz.** Cada ficha distingue cuatro capas de confianza: `medido`, `estimado`, `literatura` y `educativo`. Ver `docs/adr/ADR-0005`.

## Arquitectura y fases

- Arquitectura modular: `docs/architecture.md`
- Esquema inicial de datos: `docs/data-model.md`
- Plan de pruebas: `docs/test-plan.md`
- Entorno verificado: `docs/environment.md`
- Decisiones técnicas: `docs/adr/`
- Decisiones que requieren aprobación humana: `docs/pending-decisions.md`

| Fase | Nombre | Estado |
|---|---|---|
| 0 | Descubrimiento y arquitectura | Completada — espera aprobación |
| 1 | Sistema visual y prototipo navegable | No iniciada |
| 2 | Infraestructura de datos científicos | No iniciada |
| 3 | Perfil adaptativo y seguridad | No iniciada |
| 4 | Motor nutricional y evidencia | No iniciada |
| 5 | Gastronomía territorial y presupuesto | No iniciada |
| 6 | Bioquímica y capa explicativa | No iniciada |
| 7 | Seguimiento y modo profesional | No iniciada |
| 8 | Validación integral y preparación para producción | No iniciada |

Ninguna fase comienza sin la aprobación explícita del responsable del proyecto.

## Estructura del repositorio

```
nutri-region-colombia/
├── README.md               # este archivo
├── AGENTS.md               # reglas obligatorias para todos los agentes
├── opencode.json           # configuración mínima del proyecto (solo $schema)
├── .opencode/
│   ├── agents/             # 12 agentes especializados del proyecto
│   └── skills/             # 12 skills reutilizables
├── docs/
│   ├── architecture.md
│   ├── data-model.md
│   ├── test-plan.md
│   ├── environment.md
│   ├── opencode-agents-skills.md
│   ├── pending-decisions.md
│   └── adr/                # registro de decisiones arquitectónicas
└── data/                   # vacío por diseño hasta la Fase 2
```

Las carpetas `frontend/` y `backend/` se crearán en sus fases correspondientes con la aprobación del responsable. No existe código de aplicación todavía.

## Cómo se trabaja aquí

- El proyecto se desarrolla con OpenCode (v1.18.18) usando los agentes y skills definidos en `.opencode/`. Ver `docs/opencode-agents-skills.md` para el inventario completo.
- Las reglas obligatorias para cualquier agente están en `AGENTS.md`.
- Avance por fases con puerta de aprobación: al final de cada fase se presenta un reporte (funcionalidades, archivos, pruebas reales, fuentes, riesgos, decisiones pendientes) y el trabajo se detiene.

## Advertencias de estado

- `data/` está vacío por diseño: no hay catálogos de alimentos todavía. Se prefiere un conjunto pequeño, trazable y real antes que cientos de registros incompletos.
- Ninguna regla clínica está aprobada. Toda regla candidata es no vinculante hasta revisión profesional registrada.
- La plataforma no debe presentarse como clínicamente validada ni como avalada por OMS/OPS/ICBF mientras no exista evidencia y aprobación formal documentada.
