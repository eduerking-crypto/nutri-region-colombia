---
name: nutrition-data-validation
description: Validación de datos nutricionales para NutriRegión Colombia. Úsala al importar o modificar composición nutricional: unidades, base 100 g comestible, rangos plausibles, duplicados, valores faltantes, coherencia entre preparaciones y generación del informe de calidad.
---

# Nutrition Data Validation

## Objetivo

Que cada registro de composición publicado sea plausible, coherente, único y con procedencia completa.

## Instrucciones

1. Unidades y base: todo valor en base 100 g de porción comestible; si la fuente usa otra base, convierte y documenta el método. Declara la unidad (g, mg, µg, kcal, kJ).
2. Rangos de plausibilidad por nutriente (ej. energía ≤ 900 kcal/100 g, proteína ≤ 95 g/100 g en cualquier alimento real): los valores fuera de rango se marcan `rejected` con nota, no se "corrigen".
3. Valores faltantes: se conservan como ausentes con nota. JAMÁS se codifican como 0 ni se rellenan por intuición.
4. Duplicados: detecta por (alimento, nutriente, fuente, versión); el desempate se documenta.
5. Coherencia: energía vs. macronutrientes (Atwater aproximado como control de orden de magnitud, no como verdad exacta); crudo vs. cocido (peso/agua) cuando ambas preparaciones existan.
6. Estimaciones: todo valor `estimado` declara método (imputación, promedio de fuentes, conversión). Nunca `medido` si no viene de análisis o tabla oficial.
7. Genera el informe de calidad de cada importación: registros cargados, rechazados y por qué, cobertura de nutrientes, vacíos conocidos.

## Criterios de aceptación

- 100 % de registros con `trust_tier`, fuente, versión y fecha de consulta.
- Informe de calidad generado y revisado antes de dar por "cargada" una fuente.
- Cero valores faltantes disfrazados de cero.

## Errores que debe evitar

- "Completar" datos faltantes con promedios sin declarar el método.
- Publicar registros rechazados en validación.
- Silenciar vacíos de cobertura en los informes.
