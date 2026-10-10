# Entorno verificado — Fase 0

Fecha de verificación: 2026-10-10. Comandos ejecutados directamente en la máquina.

| Herramienta | Versión | Verificado con | Notas |
|---|---|---|---|
| OpenCode | 1.18.18 | `opencode --version` | sintaxis de agentes/skills verificada en esta instalación |
| Node.js | 24.15.0 | `node --version` | versión actual; compatibilidad con Next.js se verificará en Fase 1 antes de instalar |
| npm | 11.18.0 | `npm --version` | |
| Python (PATH) | 3.14.3 | `python --version` | satisface el requisito ≥ 3.11 del proyecto |
| Git | 2.55.0.windows.2 | `git --version` | fijar rama por defecto en `main` al inicializar |
| Ollama | 0.40.1 | `ollama --version` | candidato a proveedor IA local (ADR-0009) |
| PostgreSQL | **NO instalado** | `psql` no disponible en PATH | desarrollo local con SQLite; esquema debe ser portable (ADR-0003) |

## Implicaciones para las siguientes fases

1. **Python 3.14 es reciente**: antes de instalar cualquier dependencia en Fase 2 se debe comprobar que las ruedas (wheels) de FastAPI, SQLModel, Alembic y librerías científicas estén disponibles y fijar versiones exactas. No se instala nada sin autorización.
2. **PostgreSQL ausente**: el desarrollo local usará SQLite con SQLModel y migraciones Alembic. El esquema evita características exclusivas de cualquier motor para permanecer portable. La decisión de base de datos de producción queda pendiente (PD-07 incluye despliegue).
3. **Windows + PowerShell 5.1**: para crear/editar archivos se usan las herramientas dedicadas del agente (no cmdlets de contenido), evitando el problema de encoding UTF-8 conocido en PowerShell 5.1.
4. **Node 24 + npm 11**: compatibles con un toolchain moderno de frontend; la versión exacta de Next.js y librerías UI se elige y verifica en Fase 1 (ADR-0002).

## No verificado todavía (por diseño, sin instalación)

- No hay `package.json` ni entorno virtual: no se han instalado dependencias.
- No hay bases de datos creadas: no hay datos que proteger todavía.
- No se verificó FFmpeg ni otras herramientas ajenas al alcance de esta fase.
