# ADR-0003: Backend FastAPI + Pydantic + SQLModel; SQLite en desarrollo, PostgreSQL en producción

- **Estado:** Propuesta (pendiente de verificación de dependencias en Fase 2)
- **Fecha:** 2026-10-10

## Contexto

El backend debe validar entradas/salidas estrictamente (datos de salud), exponer contratos OpenAPI y evolucionar esquema con migraciones. El entorno verificado tiene Python 3.14.3 en PATH (satisface el requisito ≥ 3.11) y **PostgreSQL NO está instalado** en la máquina de desarrollo.

## Decisión

- FastAPI como framework de API; Pydantic para validación de contratos; SQLModel (sobre SQLAlchemy) para persistencia; Alembic para migraciones.
- Desarrollo local con SQLite. Producción multiusuario con PostgreSQL (decisión de despliegue: PD-07).
- El esquema se mantiene **portable**: sin características exclusivas de SQLite ni de PostgreSQL en la lógica de dominio; diferencias inevitables se aíslan en la capa de datos.
- Antes de instalar nada (Fase 2): verificar disponibilidad de ruedas estables de todas las dependencias para Python 3.14 y fijar versiones exactas. Si 3.14 presenta incompatibilidades, se evalúa instalar un Python 3.11/3.12 dedicado al proyecto y se documenta.

## Consecuencias

- Ventaja: contratos tipados de extremo a extremo (OpenAPI → frontend), validación estricta gratis, arranque rápido del desarrollo sin instalar PostgreSQL.
- Riesgo: SQLite enmascara diferencias de PostgreSQL (concurrencia, tipos); se mitiga con pruebas de integración contra PostgreSQL en Fase 8 y evitando SQL específico de motor.
- Riesgo: Python 3.14 es muy reciente; la verificación previa a la instalación es obligatoria (no se instala nada sin autorización).
