# Esquema inicial de datos — NutriRegión Colombia

Estado: especificación de Fase 0. El DDL real y las migraciones Alembic se crearán en Fase 2 con aprobación del responsable. Este documento define las entidades, campos mínimos, convenciones y enumeraciones que toda implementación debe respetar.

## Convenciones generales

- Fechas ISO 8601 (`YYYY-MM-DD`), moneda COP, composición por **100 g de porción comestible** salvo indicación explícita.
- IDs estables, nunca reutilizados: alimentos con prefijo de fuente (ej. `ICBF-0001`), reglas con `CR-<ambito>-<número>` (ej. `CR-ALLERG-001`), fuentes con `SRC-<sigla>`.
- Todo dato científico lleva procedencia completa (ver capa de confianza en `docs/architecture.md` y ADR-0005). Un registro sin procedencia no se publica.
- Datos personales y de salud en esquemas segregados de los datos públicos de alimentos.

## Enumeraciones

| Enum | Valores |
|---|---|
| `trust_tier` | `medido`, `estimado`, `literatura`, `educativo` |
| `verification_status` | `unverified`, `verified`, `rejected` |
| `price_data_type` | `observado`, `publicado`, `estimado` |
| `rule_status` | `candidate`, `approved`, `rejected`, `retired` |
| `region` | `caribe`, `andina`, `pacifico`, `orinoquia`, `amazonia`, `insular` |
| `food_group` | a definir en Fase 2 con la fuente oficial que se adopte; no inventar categorías |
| `allergen` | catálogo oficial de alérgenos a adoptar en Fase 3 (no inventar) |
| `dietary_pattern` | `omnivoro`, `vegetariano`, `vegano`, `otro` (autodeclarado, no diagnóstico) |

## Entidades públicas (datos científicos)

### fuente (source catalog)

| Campo | Tipo | Notas |
|---|---|---|
| `id` | string | `SRC-ICBF`, `SRC-USDA-FDC`, … |
| `name` | string | nombre oficial |
| `kind` | enum | `tabla_composicion`, `guia_alimentaria`, `publicacion`, `serie_precios`, `otro` |
| `version` | string | versión vigente usada |
| `license` | string | licencia/condiciones de uso verificadas |
| `redistribution_allowed` | bool | resultado de la verificación de licencia |
| `access_method` | enum | `api`, `descarga`, `digitalizacion`, `consulta_manual` |
| `url` / `citation` | string | identificador estable |
| `retrieved_at` | date | fecha de consulta |
| `notes` | text | limitaciones de cobertura y uso |

Regla dura: ninguna fuente se incorpora al catálogo sin `license` y `redistribution_allowed` verificados (PD-04).

### alimento (food)

| Campo | Tipo | Notas |
|---|---|---|
| `id` | string | estable, prefijo de fuente |
| `name_common` | string | nombre común |
| `name_variants` | string[] | nombres regionales/alternativos |
| `name_scientific` | string? | cuando corresponda |
| `food_group` | enum | según fuente oficial adoptada |
| `state` | string | crudo, cocido, seco, otra preparación |
| `edible_portion_pct` | decimal? | parte comestible |
| `region_associations` | enum[] | regiones donde es habitual |
| `source_ids` | string[] | identificadores en fuentes externas |
| `allergens` | enum[] | alérgenos conocidos |
| `trust_tier` / `source_id` / `retrieved_at` | procedencia | obligatorios |

### composicion_nutricional (food_nutrient)

| Campo | Tipo | Notas |
|---|---|---|
| `id` | string | |
| `food_id` | ref | |
| `nutrient` | string | nutriente o componente (energía, macro, fibra, micro, ácido graso, aminoácido, azúcar, bioactivo) |
| `value` | decimal | por 100 g de porción comestible |
| `unit` | string | g, mg, µg, kcal, kJ |
| `basis` | string | base de referencia explícita |
| `method` | string? | método/tipo de dato cuando exista |
| `trust_tier` | enum | `medido` o `estimado` (con método declarado) |
| `source_id` / `source_version` / `retrieved_at` | procedencia | obligatorios |
| `verification_status` | enum | |
| `uncertainty_notes` | text? | limitaciones conocidas |

### observacion_precio (price_observation)

| Campo | Tipo | Notas |
|---|---|---|
| `id` | string | |
| `food_id` / `product_desc` | ref/string | producto y presentación |
| `municipality` | string | municipio (código DANE) |
| `market` | string? | mercado/plaza si aplica |
| `commercial_unit` | string | unidad comercial (libra, unidad, arroba…) |
| `price_cop` | decimal | |
| `observed_at` | date | fecha de observación |
| `data_type` | `price_data_type` | observado / publicado / estimado |
| `source_id` | ref | obligatorio |
| `confidence` | string? | nivel de confianza declarado |
| `method` | text? | método de estimación si aplica |

Regla dura (ADR-0007): sin registros de precio, la UI muestra "sin datos de precio" — nunca se interpola por ubicación.

### receta (recipe) / receta_ingrediente (recipe_ingredient)

| Campo | Notas |
|---|---|
| `id`, `name`, `variant_name` | nombre y variante regional |
| `region`, `origin_notes` | procedencia cultural documentada |
| `ingredients[]` | alimento (ref) + cantidad + unidad |
| `servings` | número de porciones |
| `yield_notes` | rendimiento y cambios de peso por cocción **cuando se conozcan** |
| `steps` | preparación |
| `time_minutes`, `equipment` | tiempo y equipo |
| `nutrition_method` | método del cálculo nutricional por porción (declarado) |
| `trust_tier`, `source_id`, `retrieved_at` | procedencia obligatoria |

### referencia_evidencia (evidence)

| Campo | Notas |
|---|---|
| `id`, `citation` | referencia bibliográfica completa |
| `doi` / `pmid` / `stable_id` | identificador estable **verificado**; nunca inventado |
| `study_type` | tipo de estudio |
| `population` | población estudiada |
| `relevant_finding` | resultado relevante |
| `limitations` | limitaciones |
| `reviewed_at` | fecha de revisión |
| `food_links[]` / `claim_links[]` | relación concreta con alimentos o afirmaciones |

### regla_clinica (clinical_rule)

| Campo | Notas |
|---|---|
| `id`, `version` | ej. `CR-ALLERG-001 v2` |
| `scope` | ámbito (alergias, renal, diabetes, embarazo, interacciones, señales de alarma…) |
| `conditions` | condiciones lógicas evaluables |
| `exceptions` | excepciones |
| `action` | `bloquear_plan`, `requerir_revision_profesional`, `advertir`, `derivar_urgencia` |
| `justification`, `source_id` | justificación y fuente aplicable |
| `evidence_level` | nivel de evidencia declarado |
| `status` | `rule_status` — `candidate` por defecto |
| `reviewer`, `approved_at`, `next_review` | profesional responsable y fechas — obligatorios solo si `status=approved` |

Regla dura (ADR-0004): el motor solo ejecuta reglas con `status=approved`; las candidatas existen documentadas pero nunca se aplican.

## Entidades privadas (Fase 3+, esquema segregado)

Borrador mínimo, sujeto a revisión de privacidad (PD-03) y a minimización de datos:

- `user` — credenciales y consentimientos (qué se recogió, cuándo, versión del consentimiento).
- `user_profile` — contexto territorial (municipio DANE, urbano/rural), presupuesto y recursos, patrón de comidas, equipo de cocina, refrigeración.
- `user_preference` — preferencias, rechazos, patrón alimentario autodeclarado.
- `user_allergy` — alergia confirmada vs. intolerancia vs. reacción conocida (distinguir siempre), gravedad, verificación pendiente.
- `user_health_context` — solo con consentimiento: condiciones autorreportadas (marcadas como autorreportadas, nunca como diagnóstico), embarazo/lactancia, medicamentos relevantes.
- `professional_review` — revisiones de planes por profesionales (Fase 7).

## Ejemplo de registro con procedencia completa

```json
{
  "id": "ICBF-0001",
  "name_common": "Ejemplo pendiente de carga real",
  "note": "NO CARGAR: este bloque ilustra el formato de procedencia. data/ permanece vacío hasta la Fase 2.",
  "composition_example": {
    "nutrient": "proteina",
    "value": 0.0,
    "unit": "g",
    "basis": "100 g porción comestible",
    "trust_tier": "medido",
    "source_id": "SRC-ICBF",
    "source_version": "a fijar tras verificación",
    "retrieved_at": null,
    "verification_status": "unverified"
  }
}
```

## Reglas de calidad del esquema

1. Todo valor numérico de composición debe pasar validación de rango y plausibilidad (skill `nutrition-data-validation`).
2. Duplicados detectables por (`food_id`, `nutrient`, `source_id`, `source_version`).
3. Valores faltantes se almacenan como ausentes con nota — nunca como cero.
4. Cambios en reglas clínicas y catálogos científicos quedan en auditoría (quién, qué, cuándo, justificación).
5. Ninguna entidad pública se publica sin los campos de procedencia completos.
