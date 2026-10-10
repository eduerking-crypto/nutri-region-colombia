# data/ — Política del directorio de datos

**Este directorio está vacío por diseño.** No hay catálogos de alimentos, composiciones, precios ni recetas cargados todavía (eso ocurre en la Fase 2, con fuentes verificadas).

## Reglas de este directorio

1. Solo entra aquí un dato con procedencia completa: fuente, versión, fecha de consulta, licencia verificada y capa de confianza (`docs/data-model.md`).
2. Prohibido generar catálogos ficticios o "de ejemplo" para hacer que la aplicación parezca terminada. Los datos demo de la UI viven con el frontend, marcados visualmente como DEMO, y no se mezclan con datos reales.
3. Los datasets crudos se conservan tal como se obtuvieron, junto con el script de importación reproducible y su informe de calidad.
4. Nada se considera "cargado" hasta que el informe de calidad de la importación es revisado.

## Estructura esperada (Fase 2+)

```
data/
├── sources/    # catálogo versionado de fuentes
├── imports/    # datasets crudos + scripts + informes de calidad
└── rules/      # reglas clínicas versionadas (status: candidate hasta aprobación)
```
