"""Motor determinista de NutriRegion Colombia.

Modulos:
- calc:    calculo nutricional reproducible
- rules:   evaluador de reglas clinicas versionadas (datos, no codigo UI)
- triage:  controles de seguridad que corren ANTES de generar recomendaciones
- optimize: generador determinista de menus

Principio (ADR-0004): mismas entradas -> mismas salidas. La IA jamas entra
en esta ruta de decision.
"""
