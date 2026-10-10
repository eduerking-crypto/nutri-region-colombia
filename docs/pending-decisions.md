# Decisiones pendientes de aprobación

Registro de decisiones que **NO** puede tomar ningún agente por su cuenta. Se requieren: aprobación del responsable del proyecto (usuario), validación de un profesional sanitario o evaluación de un profesional legal, según el tipo.

| ID | Decisión pendiente | Tipo | Quién aprueba | Requerida antes de |
|---|---|---|---|---|
| PD-01 | Alcance del MVP: qué pantallas del listado de 15 entran en el mínimo viable | Producto | Usuario | Iniciar Fase 1 |
| PD-02 | Catálogo y umbrales de reglas clínicas (exclusiones, derivación, urgencias) | Clínica | Profesional sanitario competente | Habilitar cualquier regla (Fase 3/4) |
| PD-03 | Evaluación legal: Ley 1581 de 2012, consentimiento, retención y régimen aplicable a software de salud | Legal | Profesional legal | Registrar usuarios reales (Fase 3) |
| PD-04 | Fuentes de datos: verificación de licencias y permiso de redistribución (ICBF, FAO/INFOODS, USDA FDC, guías alimentarias) | Datos/Legal | Usuario + verificación documentada | Cargar datos reales (Fase 2) |
| PD-05 | Estrategia de precios: fuentes territoriales verificables (DANE/SIPSA u otras), frecuencia y método de actualización | Producto/Datos | Usuario | Fase 5 |
| PD-06 | Proveedor IA por defecto (candidato: Ollama local) y funciones habilitadas | Técnica | Usuario | Fase 6 |
| PD-07 | Despliegue y base de datos de producción (PostgreSQL), hosting, dominio | Técnica | Usuario | Fase 8 |
| PD-08 | Librería de optimización (OR-Tools vs. alternativas): decidir con prototipo medible | Técnica | Usuario (con datos del prototipo) | Fase 5 |
| PD-09 | Método de autenticación y gestión de sesión/roles | Técnica/Seguridad | Usuario (con propuesta técnica) | Fase 3 |
| PD-10 | Expectativas sobre relación con OMS/OPS/ICBF: referencia pública vs. búsqueda de colaboración formal | Producto | Usuario | Cualquier comunicación pública |
| PD-11 | Composición del comité de revisión profesional (nutrición clínica, medicina) y proceso de aprobación de reglas | Clínica | Usuario | Fase 4 |
| PD-12 | Justificación de PWA: si la utilidad real (uso offline, mercados sin conectividad) justifica el costo | Producto/Técnica | Usuario | Fase 6 |
| PD-13 | Índice de diversidad alimentaria: metodología explícita y advertencia de que NO es escala clínica validada | Científica | Usuario + revisión profesional | Presentarlo en la app (Fase 5) |
| PD-14 | API key gratuita personal de USDA FDC (registro de 2 minutos en fdc.nal.usda.gov/api-key-signup) para completar el catálogo de 28 alimentos y cargar las 10 recetas | Datos | Usuario | Cualquier momento; desbloquea Fase 5 completa |
| PD-15 | Insumos territoriales de precios: adoptar fuente oficial (DANE/SIPSA) y/o habilitar el aporte comunitario con moderación | Datos/Producto | Usuario | Fase 5 producción |

## Decisiones que el equipo técnico puede tomar (documentadas en ADR)

Estructura de carpetas, convenciones de código, formato de ADRs, nomenclatura de pruebas, organización interna de módulos, redacción de documentación. Toda decisión técnica con impacto de arquitectura o stack se registra en `docs/adr/` y las de peso se confirman con el usuario en el reporte de fase.

## Estado de las decisiones estratégicas (ya adoptadas como principios, requieren vigilancia)

1. **OMS/OPS como referencia, no certificación** — cerrada como principio (ADR-0008); cualquier paso hacia colaboración institucional pasa por PD-10.
2. **Plataforma sin fingir precios** — cerrada como principio (ADR-0007); la implementación concreta de fuentes pasa por PD-05.
3. **Confianza científica visible en la interfaz** — cerrada como principio (ADR-0005); el diseño visual concreto se aprueba en Fase 1.
