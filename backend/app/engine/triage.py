"""Triage de seguridad: se ejecuta ANTES de generar cualquier recomendacion.

Dos capas:
1. Reglas de diseno de seguridad (siempre activas, no son juicio clinico):
   exclusion de alergenos confirmados y derivacion ante sintomas de alarma.
2. Reglas clinicas versionadas (datos): solo approved; candidatas en modo piloto.

Determinista: mismas entradas -> mismas salidas (ADR-0004).
"""
from __future__ import annotations

from dataclasses import dataclass

from app.engine.rules import (
    RuleMatch,
    SafetyContext,
    apply_rules,
)
from app.models.catalog import Food
from app.models.user import UserAllergy, UserHealthFlag, UserProfile

# Severidad de estado (mayor = mas restrictivo)
STATUS_SEVERITY = {
    "ok": 0,
    "advertencia": 1,
    "requiere_profesional": 2,
    "bloqueado": 3,
    "urgencia": 4,
}

DESIGN_RULE_IDS = ("DESIGN-ALERGENOS", "DESIGN-ALARMA")


@dataclass
class SafetyMessage:
    severity: str  # advertencia | bloqueo | profesional | urgencia
    code: str
    message: str


@dataclass
class SafetyResult:
    status: str  # ok | advertencia | requiere_profesional | bloqueado | urgencia
    messages: list[SafetyMessage]
    applied_rules: list[str]
    excluded_food_ids: list[str]
    rule_matches: list[RuleMatch]


def build_context(
    profile: UserProfile | None,
    allergies: list[UserAllergy],
    health_flags: list[UserHealthFlag],
) -> SafetyContext:
    ctx = SafetyContext(onboarding_completed=bool(profile and profile.onboarding_completed))
    if profile:
        ctx.dietary_pattern = profile.dietary_pattern
        ctx.municipality = profile.municipality
    for allergy in allergies:
        ctx.allergies[allergy.allergen] = (allergy.kind, allergy.severity)
    for flag in health_flags:
        ctx.health_flags.add(flag.flag)
    return ctx


def _escalate(current: str, candidate: str) -> str:
    if STATUS_SEVERITY[candidate] > STATUS_SEVERITY[current]:
        return candidate
    return current


def evaluate_safety(
    ctx: SafetyContext, rules: list, available_foods: list[Food] | None = None
) -> SafetyResult:
    """Evalua el contexto y determina si puede generarse un plan automatico."""
    status = "ok"
    messages: list[SafetyMessage] = []
    applied: list[str] = []
    excluded: list[str] = []

    # --- Regla de diseno 1: alergenos confirmados (siempre activa) ---
    confirmed = ctx.confirmed_allergens()
    if confirmed:
        applied.append("DESIGN-ALERGENOS v1")
        severe = ctx.severe_allergens()
        if severe:
            status = _escalate(status, "advertencia")
            names = ", ".join(sorted(severe))
            messages.append(
                SafetyMessage(
                    severity="advertencia",
                    code="alergia_grave_registrada",
                    message=(
                        "Tienes registrada una alergia grave ("
                        f"{names}). Excluimos esos alimentos y sus derivados de todo "
                        "plan. Ninguna sustitucion debe considerarse segura sin "
                        "confirmar ingredientes, contaminacion cruzada y preparacion."
                    ),
                )
            )
        else:
            status = _escalate(status, "advertencia")
            names = ", ".join(sorted(confirmed))
            messages.append(
                SafetyMessage(
                    severity="advertencia",
                    code="alergia_registrada",
                    message=(
                        "Alergia confirmada registrada ("
                        f"{names}). Los alimentos que la contienen quedan excluidos "
                        "de tus planes y del explorador."
                    ),
                )
            )
        if available_foods:
            for food in available_foods:
                if set(food.allergen_list) & confirmed:
                    excluded.append(food.id)

    # --- Regla de diseno 2: sintomas de alarma (siempre activa) ---
    if "sintomas_alarma" in ctx.health_flags:
        applied.append("DESIGN-ALARMA v1")
        status = _escalate(status, "urgencia")
        messages.append(
            SafetyMessage(
                severity="urgencia",
                code="sintomas_alarma",
                message=(
                    "Registraste senales que pueden requerir atencion medica "
                    "inmediata. NutriRegion no genera planes alimentarios en este "
                    "caso. Por favor busca atencion sanitaria cuanto antes; si los "
                    "sintomas son intensos, acude a urgencias."
                ),
            )
        )

    # --- Reglas clinicas versionadas ---
    matches = apply_rules(ctx, rules)
    for match in matches:
        applied.append(f"{match.rule_id} v{match.version}")
        if match.action == "derivar_urgencia":
            status = _escalate(status, "urgencia")
            messages.append(SafetyMessage("urgencia", match.rule_id, match.message))
        elif match.action == "bloquear":
            status = _escalate(status, "bloqueado")
            messages.append(SafetyMessage("bloqueo", match.rule_id, match.message))
        elif match.action == "derivar_profesional":
            status = _escalate(status, "requiere_profesional")
            messages.append(SafetyMessage("profesional", match.rule_id, match.message))
        elif match.action == "advertir":
            status = _escalate(status, "advertencia")
            messages.append(SafetyMessage("advertencia", match.rule_id, match.message))

    if not ctx.onboarding_completed and status == "ok":
        status = _escalate(status, "advertencia")
        messages.append(
            SafetyMessage(
                severity="advertencia",
                code="perfil_incompleto",
                message=(
                    "Tu perfil esta incompleto: completa el cuestionario inicial "
                    "para recomendaciones ajustadas a tu territorio, presupuesto y "
                    "preferencias."
                ),
            )
        )

    MESSAGE_ORDER = {"urgencia": 0, "bloqueo": 1, "profesional": 2, "advertencia": 3}
    messages.sort(key=lambda msg: (MESSAGE_ORDER[msg.severity], msg.code))
    return SafetyResult(
        status=status,
        messages=messages,
        applied_rules=applied,
        excluded_food_ids=sorted(set(excluded)),
        rule_matches=matches,
    )


def food_allergy_conflicts(food: Food, ctx: SafetyContext) -> list[dict]:
    """Conflictos de un alimento concreto con las alergias del usuario."""
    conflicts = []
    for allergen in sorted(set(food.allergen_list) & set(ctx.allergies)):
        kind, severity = ctx.allergies[allergen]
        conflicts.append({"allergen": allergen, "kind": kind, "severity": severity})
    return conflicts
