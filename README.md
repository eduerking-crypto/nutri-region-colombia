# NutriRegión Colombia

Plataforma digital de nutrición territorial: recomendaciones alimentarias contextualizadas en el territorio, el presupuesto, la cultura gastronómica y las necesidades individuales de las personas en Colombia, con rigor científico trazable.

> **Estado: Fases 0–7 construidas (v0.1.0). Pendiente de validación profesional y de despliegue en producción.**
> Motor determinista probado (108 pruebas, cobertura > 90 % en el módulo crítico), 8 alimentos reales con procedencia completa, 16 pantallas funcionales verificadas en accesibilidad y calidad visual. **No está clínicamente validado** (ver Advertencias).

## Cómo ejecutar (desarrollo)

```bash
# Backend (puerto 8400)
cd backend
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt -r requirements-dev.txt email-validator
copy .env.example .env      # ajusta valores; NUTRI_AUTOSEED no es necesario (ver seed)
.venv\Scripts\python -m app.seed        # carga alimentos reales, reglas candidatas y admin
.venv\Scripts\python -m uvicorn app.main:app --port 8400

# Frontend (puerto 3000, proxy /api -> 8400)
cd frontend
npm install
npm run build && npm start       # o: npm run dev

# Pruebas del backend (108, con cobertura)
cd backend && .venv\Scripts\python -m pytest tests --cov=app
```

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
- Esquema de datos: `docs/data-model.md`
- Plan de pruebas: `docs/test-plan.md`
- Entorno verificado: `docs/environment.md`
- Decisiones técnicas: `docs/adr/`
- Decisiones que requieren aprobación humana: `docs/pending-decisions.md`

| Fase | Nombre | Estado |
|---|---|---|
| 0 | Descubrimiento y arquitectura | Completada |
| 1 | Sistema visual y prototipo navegable | Construida — 16 pantallas, build limpio, auditoría de accesibilidad 12/12, revisión visual con IA 7–9/10 |
| 2 | Infraestructura de datos científicos | Construida — importador reproducible USDA FDC + informe de calidad + Alembic baseline |
| 3 | Perfil adaptativo y seguridad | Construida — auth JWT + roles, consentimiento, alergias, triage con catálogo adverso probado |
| 4 | Motor nutricional y evidencia | Construida — motor determinista (calc/rules/triage/optimize), reglas aplicadas trazables |
| 5 | Gastronomía territorial y presupuesto | Parcial — precios honestos (sin datos = "sin datos") y sustituciones funcionan; recetas esperan ingredientes; optimizador v1 greedy |
| 6 | Bioquímica y capa explicativa | Parcial — fichas con capas de confianza por nutriente; IA implementada y desactivada por defecto |
| 7 | Seguimiento y modo profesional | Construida — seguimiento, panel profesional con aprobación de reglas, export/eliminación de cuenta |
| 8 | Validación integral y producción | En curso — pruebas y auditorías técnicas ejecutadas; validación clínica/legal pendiente (externa) |

**Estado real del catálogo:** 8 alimentos con datos reales (USDA FDC, límite 10 descargas/día de la DEMO_KEY). Con una [API key gratuita personal de FDC](https://fdc.nal.usda.gov/api-key-signup) y ejecutar `python scripts/fetch_fdc.py --key TU_CLAVE` + `python -m app.seed`, el catálogo crece a 28 alimentos y las 10 recetas cargan solas. Nunca inventamos alimentos para llenar la pantalla.

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
