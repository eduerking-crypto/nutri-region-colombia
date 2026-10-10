# ADR-0007: Precios territoriales honestos — la plataforma no finge conocer precios

- **Estado:** Aceptada (Fase 0) — decisión estratégica del responsable
- **Fecha:** 2026-10-10

## Contexto

Decisión estratégica del proyecto: los precios y la disponibilidad territorial pueden ser la característica más innovadora de la app, pero también la más difícil de resolver con rigor. No existe hoy una fuente pública completa y actualizada de precios por mercado municipal colombiano. Inferir precios a partir de la ubicación o inventar "promedios" destruiría la confianza y daría presupuestos falsos.

## Decisión

1. Todo precio mostrado proviene de un registro `observacion_precio` con: fecha de observación, tipo de dato (`observado` / `publicado` / `estimado`), fuente y, si es estimado, método declarado.
2. Prohibido interpolar o deducir precios a partir de la geografía (municipio, departamento) o de promedios no documentados.
3. La plataforma **funciona completamente sin datos de precio**: menús, fichas, recetas y orientación alimentaria operan; solo las funciones de presupuesto se degradan honestamente mostrando "sin datos de precio para este municipio" y la fecha/naturaleza de la última estimación disponible, si existe.
4. La estrategia de captura e integración de precios (fuentes oficiales como DANE/SIPSA, observación directa documentada, etc.) es una decisión pendiente (PD-05, Fase 5).
5. Nunca se garantiza el cumplimiento de un presupuesto cuando faltan precios o las unidades no son comparables.

## Consecuencias

- Ventaja: cada peso mostrado en la app es defendible; el usuario sabe exactamente qué tan confiable es el número que ve.
- Costo: la función estrella (presupuesto por municipio) dependerá de la calidad de los datos que se logre conseguir; el diseño asume desde ya esa limitación en lugar de falsearla.
- Requisito de UI: el tipo y fecha del dato de precio son visibles junto al número, no en letra pequeña.
