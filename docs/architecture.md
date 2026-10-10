# Arquitectura — NutriRegión Colombia

Estado: propuesta técnica de Fase 0, pendiente de aprobación del responsable. Cada decisión relevante tiene su ADR en `docs/adr/`.

## Visión general

```
┌──────────────────────────────────────────────────────────────┐
│                    CAPA DE CONFIANZA (transversal)             │
│   trust_tier: medido | estimado | literatura | educativo      │
│   procedencia: fuente + versión + fecha + estado de verificación│
└──────────────────────────────────────────────────────────────┘
        ▲                ▲                  ▲
        │                │                  │
┌───────┴──────┐  ┌──────┴───────┐  ┌───────┴─────────┐
│   frontend/   │  │   backend/   │  │     data/       │
│ Next.js + TS  │◄─┤ FastAPI      │◄─┤ fuentes →       │
│ Tailwind,     │  │ Pydantic,    │  │ importadores →  │
│ Motion,       │  │ SQLModel,     │  │ validación →    │
│ Recharts      │  │ motor         │  │ catálogo        │
└───────────────┘  │ determinista  │  │ versionado      │
                   └──────────────┘  └─────────────────┘
```

Flujo de datos: fuente externa → importador reproducible → validación de calidad → catálogo versionado → motor determinista → API → UI con capas de confianza visibles.

## Módulos

### 1. frontend/ (Fase 1)

- Next.js + React + TypeScript, App Router.
- Tailwind CSS + biblioteca de componentes accesibles (se evaluará shadcn/ui u otra en Fase 1).
- Motion (Framer Motion) para animaciones respetando `prefers-reduced-motion`.
- Recharts para visualización de datos.
- Formularios con validación de esquemas (react-hook-form + zod, a confirmar en Fase 1).
- Diseño responsive (móvil, tablet, escritorio). PWA solo cuando se justifique (PD-12).

### 2. backend/ (Fase 2+)

FastAPI con capas internas:

- `app/api/` — routers y contratos (OpenAPI autogenerado).
- `app/services/` — lógica de dominio (perfil, menús, sustituciones, compras).
- `app/engine/` — módulo crítico, aislado y probado:
  - `triage/` — controles de seguridad y derivación profesional (se ejecuta ANTES de generar cualquier recomendación individualizada).
  - `rules/` — motor determinista de reglas clínicas versionadas (datos, no código hardcodeado).
  - `calc/` — cálculo nutricional reproducible a partir de ingredientes y porciones.
  - `optimize/` — optimización de menús (librería por decidir, ADR-0010).
- `app/models/` — SQLModel + migraciones Alembic.
- `app/security/` — autenticación, roles, auditoría.
- `tests/` — pytest (unit, integración, propiedad, adversarial).

### 3. data/ (Fase 2+)

- `sources/` — catálogo de fuentes versionado (tabla ICBF, FAO/INFOODS, USDA FDC, guías alimentarias…), con licencia, versión, fecha de consulta y método de acceso.
- `imports/` — datasets crudos tal como se obtuvieron + scripts de importación reproducibles + informes de calidad generados.
- `rules/` — definiciones versionadas de reglas clínicas (YAML/JSON), con estado `candidate` hasta aprobación profesional.

### 4. docs/ (vivo)

Documentación de arquitectura, datos, pruebas, ADRs y decisiones pendientes. Se actualiza en cada fase.

### 5. .opencode/ (completo)

12 agentes y 12 skills del proyecto (ver `docs/opencode-agents-skills.md`). Configuración de alcance proyecto: no modifica nada global.

## Capa transversal de confianza

Todos los datos científicos del sistema cruzan la misma interfaz de procedencia (ADR-0005):

| Campo | Valores |
|---|---|
| `trust_tier` | `medido`, `estimado`, `literatura`, `educativo` |
| `source_id` | referencia al catálogo de fuentes |
| `source_version` | versión de la fuente usada |
| `retrieved_at` | fecha de consulta (ISO 8601) |
| `verification_status` | `unverified`, `verified`, `rejected` |

La UI debe mostrar el tier visualmente en cada ficha, precio, afirmación de evidencia y explicación. Un dato sin procedencia completa no se publica.

## Contratos

- API REST JSON con esquema OpenAPI autogenerado desde Pydantic (ADR-0003).
- Contratos validados en ambos extremos: los tipos de frontend se generan o verifican contra el esquema (skill `api-contract-validation`).
- Cambios de contrato no compatibles requieren ADR y versión de API.

## Seguridad (resumen)

- Autenticación y roles: `usuario`, `profesional`, `admin` (método concreto: PD-09, Fase 3).
- Segregación estricta entre datos personales/salud y datos públicos de alimentos.
- Auditoría de cambios en reglas clínicas y datos científicos (quién, qué, cuándo, justificación).
- Secretos solo por variables de entorno. Validación de entradas en todo el perímetro.
- Evaluación de cumplimiento colombiano (Ley 1581 de 2012 y demás normas aplicables) por profesional legal (PD-03).

## Inteligencia artificial (resumen)

- Interfaz desacoplada de proveedor; candidato por defecto: Ollama local (v0.40.1 verificado).
- Desactivable sin interrumpir las funciones nutricionales esenciales.
- Nunca en la ruta de seguridad ni de cálculo: explica datos ya verificados (ADR-0004, ADR-0009).

## Decisiones técnicas (índice)

| # | Decisión | ADR |
|---|---|---|
| 1 | Monorepo modular | ADR-0001 |
| 2 | Frontend Next.js + TypeScript | ADR-0002 |
| 3 | Backend FastAPI + Pydantic + SQLModel; SQLite dev / PostgreSQL prod | ADR-0003 |
| 4 | Motor determinista separado de la IA | ADR-0004 |
| 5 | Capas de confianza y procedencia obligatoria | ADR-0005 |
| 6 | Prohibición de datos ficticios presentados como reales | ADR-0006 |
| 7 | Precios territoriales honestos | ADR-0007 |
| 8 | OMS/OPS como referencia, no certificación | ADR-0008 |
| 9 | IA desacoplada, opcional, sin API de pago obligatoria | ADR-0009 |
| 10 | Selección de optimizador diferida a prototipo medible | ADR-0010 |

## Estructura de carpetas objetivo (Fase 1+)

```
nutri-region-colombia/
├── frontend/                 # Fase 1
├── backend/                  # Fase 2
│   ├── app/
│   │   ├── api/
│   │   ├── services/
│   │   ├── engine/           # triage, rules, calc, optimize
│   │   ├── models/
│   │   └── security/
│   └── tests/
├── data/
│   ├── sources/
│   ├── imports/
│   └── rules/
├── docs/
└── .opencode/
```

Las carpetas de código se crean vacías en su fase correspondiente; no se pre-genera código antes de tiempo.
