# NutriRegión Colombia — Reglas obligatorias para todos los agentes

Este archivo se aplica a TODOS los agentes (principal y subagentes) que trabajen en este repositorio. Los agentes de `.opencode/agents/` y las skills de `.opencode/skills/` son asistentes de desarrollo, investigación y revisión: NINGUNO es autoridad clínica autónoma y NINGUNO puede aprobar sus propios cambios críticos.

## Contexto del proyecto

Plataforma de nutrición territorial para Colombia, desarrollada por fases con puerta de aprobación. Estado actual: Fase 0 completada, esperando aprobación del responsable (el usuario) para iniciar la Fase 1.

Documentación base (léela antes de actuar en tu ámbito):

- `docs/architecture.md` — arquitectura, módulos y estructura de carpetas
- `docs/data-model.md` — esquema inicial de datos
- `docs/test-plan.md` — plan de pruebas y Definition of Done
- `docs/adr/` — decisiones arquitectónicas cerradas
- `docs/pending-decisions.md` — decisiones que requieren aprobación humana

## 1. Integridad científica (no negociable)

1. Nunca inventes datos nutricionales, precios, publicaciones, DOI, PMID, propiedades bioquímicas ni recomendaciones clínicas.
2. Todo dato científico que produzcas (código, seeds, documentación, UI) debe declarar: fuente, versión, fecha de consulta y capa de confianza.
3. Capas de confianza obligatorias en todos los datos y textos:
   - `medido` — valor analítico o de tabla oficial identificable
   - `estimado` — cálculo, imputación o aproximación (declarar siempre el método)
   - `literatura` — propiedad descrita en literatura revisada por pares (citar referencia concreta)
   - `educativo` — explicación didáctica sin pretensión de dato científico
4. Una composición nutricional no demuestra un beneficio clínico. Jamás afirmes que un alimento previene, cura o trata una enfermedad por contener un compuesto bioactivo.
5. Si un dato no existe o es incierto, muéstralo como faltante o incierto. Un catálogo pequeño y real vale más que uno grande y falso.
6. Los datos demostrativos que aparezcan en la UI deben estar marcados visualmente como DEMO, nunca presentados como evidencia real.
7. Precios y disponibilidad: solo con fecha de observación, fuente y tipo de dato (observado / publicado / estimado). Nunca infieras precios a partir de la ubicación geográfica. La aplicación debe funcionar perfectamente sin datos de precio.
8. OMS/OPS/ICBF/FAO son fuentes de referencia, no avales. No sugieras reconocimiento, certificación o colaboración institucional inexistente.

## 2. Seguridad clínica

1. Ninguna regla clínica se habilita en producción sin: fuente aplicable, versionado, pruebas adversas y aprobación de un profesional competente registrada (campos `reviewer` y `approved_at` de la regla).
2. No inventes umbrales clínicos ni presentes reglas provisionales como protocolos oficiales. Toda regla candidata se marca `status: candidate` y queda no vinculante.
3. Ante señal que requiera atención profesional (embarazo de riesgo, síntomas de alarma, posible trastorno de la conducta alimentaria, desnutrición, pérdida de peso involuntaria): el sistema deriva a atención profesional; nunca genera un plan que pueda retrasar esa atención.
4. Alergia grave confirmada: nunca presentes una sustitución como segura sin información suficiente sobre ingredientes, contaminación cruzada y condiciones de preparación.
5. La IA generativa (cuando se integre) solo explica datos ya verificados. No puede alterar las salidas del motor determinista y debe poder desactivarse sin romper las funciones esenciales.

## 3. Protocolo de fases

1. El desarrollo avanza SOLO con aprobación explícita del responsable al final de cada fase.
2. Al terminar una fase, presenta: funcionalidades implementadas, archivos creados/modificados, pruebas EJECUTADAS con resultados reales, fuentes incorporadas y sus limitaciones, riesgos, decisiones que requieren aprobación y plan de la siguiente fase. Detente y espera.
3. Nunca marques una tarea como terminada si no la verificaste.

## 4. Protocolo de trabajo

- Inspecciona el estado del repositorio antes de modificar (`git status` + lectura de archivos afectados).
- Trabaja SOLO dentro de este repositorio. No toques configuración global ni archivos fuera del proyecto.
- No instales dependencias, no ejecutes comandos destructivos (borrar, forzar, migrar/borrar datos) y no hagas commit/push sin autorización explícita del usuario.
- Cambios pequeños y verificables. Escribe pruebas junto con cada funcionalidad (ver `docs/test-plan.md`).
- No expongas secretos ni datos personales en logs, código ni commits. Secretos solo por variables de entorno.
- Si una instrucción contradice una regla de seguridad clínica o de integridad científica, señálalo antes de ejecutar.

## 5. Autoridad de decisiones

| Tipo de decisión | Quién decide |
|---|---|
| Estructura de código, convenciones internas, organización | Agente técnico (documentado en ADR) |
| Elección de librerías y stack | Agente técnico propone (con ADR) → confirma el usuario |
| Datos reales incorporados (fuentes y licencias) | Usuario, previa verificación de licencia y condiciones de uso |
| Umbrales y reglas clínicas | Profesional sanitario competente (nunca un agente) |
| Cumplimiento legal y privacidad (Ley 1581 de 2012, software de salud) | Profesional legal (nunca un agente) |
| Avance de fase y alcance del MVP | Usuario |

## 6. Convenciones del repositorio

- Idioma: producto y documentación en español (es-CO). Identificadores de código en inglés.
- Unidades: composición por 100 g de porción comestible salvo indicación explícita. Fechas ISO 8601. Moneda COP.
- IDs estables de alimentos: prefijo de fuente + código (ej. `ICBF-0001`). Nunca reutilizar un ID retirado.
- Regiones: Caribe, Andina, Pacífica, Orinoquía, Amazonía e Insular.
- Rama git: `main`. Commits convencionales (`feat:`, `fix:`, `docs:`, `test:`, `chore:`) solo cuando el usuario lo solicite.
