# ADR-0002: Frontend con Next.js + TypeScript

- **Estado:** Propuesta (pendiente de verificación de versiones exactas en Fase 1)
- **Fecha:** 2026-10-10

## Contexto

El producto es una plataforma web con estado de aplicación complejo, visualizaciones de datos científicos, formularios por fases (onboarding adaptativo) y requisitos fuertes de accesibilidad. El prompt maestro fija la dirección (Next.js, React, TypeScript, Tailwind, Motion, Recharts) y el entorno verificado tiene Node 24.15.0 / npm 11.18.0.

## Decisión

Adoptar Next.js (App Router) + React + TypeScript como base del frontend, con Tailwind CSS para estilos, Motion para animaciones controladas y Recharts para gráficos. La biblioteca de componentes accesibles (p. ej. shadcn/ui u otra) y la combinación de validación de formularios (p. ej. react-hook-form + zod) se elegirán y verificarán en Fase 1 con un prototipo ejecutable antes de comprometer el stack completo. La PWA queda diferida hasta justificación (PD-12).

## Consecuencias

- Ventaja: ecosistema maduro, SSR/RSC para fichas públicas de alimentos (SEO y carga en zonas de conectividad limitada) y tipado fuerte alineado con los contratos de API.
- Costo: complejidad de build; se acota con una estructura de app simple y componentes poco acoplados.
- Condición: si la verificación de Fase 1 revela incompatibilidades serias con Node 24 o problemas de accesibilidad en la biblioteca elegida, se documenta un ADR de reemplazo en lugar de forzar la decisión.
