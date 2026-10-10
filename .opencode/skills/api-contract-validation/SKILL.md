---
name: api-contract-validation
description: Validación de contratos de API para NutriRegión Colombia. Úsala al definir, modificar o consumir endpoints: esquemas OpenAPI/Pydantic, coherencia con los tipos de frontend, manejo de errores y detección de cambios rompientes.
---

# API Contract Validation

## Objetivo

Frontend y backend hablan exactamente el mismo idioma, versionado y verificable.

## Instrucciones

1. Contrato único: el esquema OpenAPI se genera desde los modelos Pydantic (fuente de verdad); nada de documentación manual divergente.
2. Todo endpoint declara: request validado, response tipado, errores posibles con su semántica (400 validación, 401/403 acceso, 404 ausencia, 409 conflicto, 422 semántica de negocio, 500 nunca filtrado al usuario).
3. Procedencia en el contrato: todo payload de datos científicos incluye los campos de capa de confianza y fuente — el contrato no permite "dato pelado".
4. Estados "sin datos": el contrato define la representación de ausencia (null + reason, no 0 ni string vacío).
5. Frontend: los tipos se generan o verifican contra el esquema en cada cambio; desviación = error de build.
6. Cambios rompientes: requieren ADR + versión de API + migración coordinada con `frontend-specialist`; los aditivos se documentan en changelog de contrato.
7. Pruebas de contrato: cada endpoint tiene al menos prueba de happy path + validación + error de autorización.

## Criterios de aceptación

- Esquema OpenAPI actualizado y commiteado en cada cambio.
- Cero tipos duplicados a mano en frontend que contradigan el esquema.
- Errores con mensajes accionables en español es-CO.

## Errores que debe evitar

- Endpoints "temporales" sin contrato.
- Cambiar el esquema sin verificar el impacto en pantallas existentes.
- Silenciar errores devolviendo 200 con cuerpo de error.
