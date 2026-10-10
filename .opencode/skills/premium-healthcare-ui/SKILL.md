---
name: premium-healthcare-ui
description: Dirección visual premium de productos de salud para NutriRegión Colombia. Úsala al diseñar o revisar pantallas, sistemas visuales, tokens, animaciones o microinteracciones. Exige estética editorial clínica, confianza científica visible y respeto por prefers-reduced-motion.
---

# Premium Healthcare UI

## Objetivo

Una interfaz que transmita la confianza de una plataforma científica con la cercanía de la gastronomía colombiana — con estándar de producto premium, no de plantilla.

## Instrucciones

1. Dirección visual editorial contemporánea:
   - Fondos marfil y blancos cálidos; verde salvia y botánico; acentos tierra de saturación moderada.
   - Tipografía legible con jerarquías claras; tarjetas con espacios generosos y bordes sutiles.
   - Iconografía consistente; fotografía real de alimentos cuando exista (representación regional auténtica).
   - Prohibido: saturación de tarjetas, colores estridentes, gradientes excesivos, apariencia de plantilla genérica.
2. La confianza científica es diseño: las capas de confianza (`medido`/`estimado`/`literatura`/`educativo`), la fecha y naturaleza de los precios, y los estados "sin datos" tienen tratamiento visual claro y consistente en TODA la app (ADR-0005/0006/0007).
3. Animaciones: transiciones suaves entre pantallas, aparición progresiva, microinteracciones en botones/filtros/selectores, indicadores de progreso en cuestionarios, skeletons solo cuando de verdad se carga. Nunca retrasan tareas clínicas ni ocultan información.
4. Accesibilidad desde el diseño: contraste, foco visible, áreas táctiles, lenguaje claro es-CO, cero estigmatización (peso, ingresos, cultura).
5. Estados completos por pantalla: carga, vacío, error, éxito, sin datos, sin conexión de función (IA desactivada).
6. Documenta tokens (color, tipografía, espaciado, radio, movimiento) para sobrevivir entre sesiones y agentes.

## Criterios de aceptación

- Toda pantalla pasa revisión responsive (móvil/tablet/escritorio) y de contraste.
- `prefers-reduced-motion` respetado en el 100 % de las animaciones.
- El usuario distingue capas de confianza sin leer documentación.

## Errores que debe evitar

- Diseños que oculten la incertidumbre de los datos para verse "más completos".
- Animación decorativa en flujos de seguridad o derivación profesional.
- Modas visuales que rompen la sobriedad clínica del producto.
