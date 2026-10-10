---
name: privacy-security-audit
description: Auditoría de privacidad y seguridad para NutriRegión Colombia. Úsala al diseñar o revisar autenticación, roles, datos personales o de salud, consentimientos, registros, secretos y protección de datos (Ley 1581 de 2012). Prepara la evaluación para revisión legal profesional; no declara cumplimiento.
---

# Privacy Security Audit

## Objetivo

Proteger los datos de las personas — en especial los de salud — con minimización, control de acceso y evidencia auditable.

## Instrucciones

1. Minimización: revisa cada dato solicitado por la app contra su función concreta ("¿para qué lo necesito?"). Peso, talla, fotos corporales o biomarcadores NO se exigen para orientación alimentaria general.
2. Segregación: datos personales/salud separados físicamente de los datos públicos de alimentos; el acceso cruzado queda prohibido por diseño.
3. Consentimiento: versionado, específico por finalidad, revocable; registrar qué se consintió, cuándo y con qué versión del texto.
4. Derechos: exportación y eliminación de cuenta diseñadas desde el inicio, no a destiempo; política de retención explícita.
5. Control de acceso: roles usuario/profesional/admin; aislamiento entre usuarios probado (nadie lee datos ajenos).
6. Secretos y logs: solo variables de entorno; jamás datos personales, tokens ni diagnósticos en logs o commits.
7. Perímetro: validación de entradas en todos los endpoints; protección OWASP Top 10 revisada por fase.
8. Auditoría: cambios en reglas clínicas y datos científicos dejan registro (quién, qué, cuándo, justificación).
9. Ley 1581 de 2012 y normas aplicables: mantén el checklist de verificación listo para profesional legal (PD-03). El equipo técnico NO declara cumplimiento legal.

## Criterios de aceptación

- Ningún dato personal sin finalidad documentada ni consentimiento asociado.
- Pruebas de aislamiento multiusuario pasando.
- Checklist legal actualizado y pendiente de firma profesional registrado como riesgo abierto hasta que ocurra.

## Errores que debe evitar

- Afirmar "cumple la Ley 1581" — eso lo evalúa un profesional legal.
- Recolectar datos de salud "por si acaso sirven después".
- Logs verbosos con datos sensibles "temporales".
