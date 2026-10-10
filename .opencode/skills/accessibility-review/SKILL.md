---
name: accessibility-review
description: Revisión de accesibilidad (WCAG 2.2 AA) para NutriRegión Colombia. Úsala al construir o revisar cualquier pantalla, componente, formulario, gráfico o flujo interactivo. Cubre teclado, contraste, lectores de pantalla, prefers-reduced-motion y contenido en español claro.
---

# Accessibility Review

## Objetivo

Que la plataforma sea usable por todas las personas, incluidas quienes usan lector de pantalla, navegación por teclado o movimiento reducido.

## Instrucciones

1. Base normativa: WCAG 2.2 nivel AA como mínimo verificable.
2. Semántica: landmarks y jerarquía de encabezados correctos; etiquetas asociadas a todo campo; `aria-*` solo cuando la semántica nativa no alcanza.
3. Teclado: todo interactivo alcanzable, operable y con foco visible; sin trampas de foco; orden lógico en onboarding y cuestionarios.
4. Contraste: texto e iconos informativos sobre fondo cumplen AA; los estados de foco y error también.
5. Lectores de pantalla: nombre, rol y valor en controles; anuncios de cambios de estado; gráficos con alternativa textual (no solo `alt` decorativo).
6. Movimiento: `prefers-reduced-motion` desactiva animaciones no esenciales; sin parallax obligatorio ni movimiento que distraiga en flujos clínicos.
7. Formularios de salud: errores identificables, descritos en texto y corregibles; nunca dependen solo de color.
8. Lenguaje: español claro es-CO, sin jerga clínica sin explicación; términos de salud definidos en el propio texto.

## Criterios de aceptación

- Auditoría automática (axe) sin errores críticos en cada pantalla entregada.
- Recorrido completo del flujo principal solo con teclado.
- Cada fase reporta qué se verificó y qué quedó pendiente.

## Errores que debe evitar

- Dejar accesibilidad "para el final" — se revisa en cada entrega.
- Usar color como único canal de información.
- Skeletons o spinners sin rol/estado anunciado.
