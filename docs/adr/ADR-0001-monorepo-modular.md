# ADR-0001: Monorepo modular

- **Estado:** Aceptada (Fase 0)
- **Fecha:** 2026-10-10

## Contexto

El proyecto tiene cuatro dominios muy acoplados a un mismo producto: interfaz, API, datos científicos y documentación viva. Los agentes trabajan por fases con reportes frecuentes y el responsable revisa resultados concretos; dividir en varios repositorios multiplicaría la fricción sin beneficio en esta etapa (no hay equipos separados ni despliegues independientes).

## Decisión

Un único repositorio (`nutri-region-colombia`) con módulos de primer nivel separados: `frontend/`, `backend/`, `data/`, `docs/`, `.opencode/`. Cada módulo tiene responsabilidades y fases propias. No se pre-generan carpetas de código antes de su fase.

## Consecuencias

- Ventaja: cambios transversales (contrato, esquema, reglas) se versionan juntos; la trazabilidad de fases es directa.
- Ventaja: los agentes y skills comparten contexto de todo el producto.
- Riesgo: acoplamiento accidental entre módulos; se mitiga con contratos explícitos (OpenAPI, schemas) y ADRs de frontera.
- Si el proyecto creciera hacia equipos independientes, separar `data/` o `frontend/` sería la primera frontera natural.
