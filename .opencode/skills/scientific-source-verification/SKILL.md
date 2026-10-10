---
name: scientific-source-verification
description: Verificación de fuentes científicas para NutriRegión Colombia. Úsala ANTES de citar o incorporar cualquier fuente (tablas de composición, guías, publicaciones, series de precios) y siempre que se vaya a registrar un DOI, PMID o referencia bibliográfica. Protocolo anti-invención de referencias.
---

# Scientific Source Verification

## Objetivo

Garantizar que toda fuente usada en el proyecto existe, es verificable, está en su versión vigente y su licencia permite el uso previsto.

## Instrucciones

1. Identifica la fuente con su nombre oficial exacto y su editor (ICBF, FAO/INFOODS, USDA FDC, revista, organismo).
2. Verifica la versión vigente y la fecha de publicación/actualización; regístralas.
3. Verifica el método de acceso real (API, descarga, digitalización, consulta manual) y qué tan reproducible es.
4. Verifica la licencia y el permiso de redistribución; si no es explícito, márcalo `redistribution_allowed: null` y escala a PD-04 — no asumas permiso.
5. Para publicaciones: verifica DOI/PMID contra la fuente real (resolución de DOI, PubMed). Si un identificador no se puede verificar, la referencia NO se usa.
6. Registra en `data/sources/`: id, nombre, versión, licencia, acceso, URL/cita, fecha de consulta, limitaciones de cobertura.
7. Registra la fecha de consulta y planifica re-verificación si la fuente cambia.

## Criterios de aceptación

- La entrada del catálogo de fuentes tiene todos los campos, con fecha.
- Ningún DOI/PMID/cita en el proyecto carece de verificación documentada.
- Las limitaciones de la fuente están escritas (cobertura geográfica, año, metodología).

## Errores que debe evitar

- Inventar o "reconstruir" referencias, DOI, PMID, títulos o resultados por plausible que parezcan.
- Citar una fuente de oídas (por memoria) sin verificarla en esta sesión.
- Asumir que una fuente pública permite redistribución de sus datos.
- Mezclar versiones de una fuente sin declarar cuál se usó en cada dato.
