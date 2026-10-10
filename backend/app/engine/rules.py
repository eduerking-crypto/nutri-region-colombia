"""Evaluador de reglas clinicas versionadas (ADR-0004).

Las reglas viven en la base de datos (sembradas desde data/rules/).
El motor solo aplica reglas con status=approved; en modo piloto tambien evalua
candidatas (visible en la UI con un banner). Ninguna regla candidata se
considera aprobada.
"""
from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field

from app.models.rules import ClinicalRule

ACTION_SEVERITY = {
    "advertir": 1,
    "derivar_profesional": 2,
    "bloquear": 3,
    "derivar_urgencia": 4,
}

STATUS_APPROVED = "approved"
STATUS_CANDIDATE = "candidate"


@dataclass
class SafetyContext:
    """Entrada determinista del motor de reglas, derivada del perfil."""

    health_flags: set[str] = field(default_factory=set)
    # allergen -> (kind, severity)
    allergies: dict[str, tuple[str, str]] = field(default_factory=dict)
    dietary_pattern: str = "omnivoro"
    municipality: str | None = None
    onboarding_completed: bool = False

    def confirmed_allergens(self) -> set[str]:
        return {
            allergen
            for allergen, (kind, _severity) in self.allergies.items()
            if kind == "alergia_confirmada"
        }

    def severe_allergens(self) -> set[str]:
        return {
            allergen
            for allergen, (kind, severity) in self.allergies.items()
            if kind == "alergia_confirmada" and severity == "alta"
        }


@dataclass
class RuleMatch:
    rule_id: str
    version: int
    scope: str
    name: str
    action: str
    message: str
    justification: str
    status: str
    source_desc: str


def evaluate_condition(condition: dict, ctx: SafetyContext) -> bool:
    """Evalua una condicion atomica contra el contexto."""
    ctype = condition.get("type")
    value = condition.get("value")
    if ctype == "health_flag":
        return value in ctx.health_flags
    if ctype == "allergy":
        kind = condition.get("kind", "alergia_confirmada")
        present = ctx.allergies.get(value)
        return present is not None and present[0] == kind
    if ctype == "dietary_pattern":
        return ctx.dietary_pattern == value
    if ctype == "no_onboarding":
        return not ctx.onboarding_completed
    return False


def rule_applies(rule: ClinicalRule, ctx: SafetyContext) -> bool:
    """Todas las condiciones deben cumplirse y ninguna excepcion debe aplicar."""
    conditions = rule.conditions_list
    if not conditions:
        return False  # una regla sin condiciones no es evaluable
    if not all(evaluate_condition(cond, ctx) for cond in conditions):
        return False
    if any(evaluate_condition(exc, ctx) for exc in rule.exceptions_list):
        return False
    return True


def load_active_rules(session, pilot_mode: bool) -> list[ClinicalRule]:
    """Reglas activas: aprobadas siempre; candidatas solo en modo piloto."""
    from sqlmodel import select

    rules = list(session.exec(select(ClinicalRule)).all())
    active = []
    for rule in rules:
        if rule.status == STATUS_APPROVED:
            active.append(rule)
        elif pilot_mode and rule.status == STATUS_CANDIDATE:
            active.append(rule)
    # Orden estable por id para determinismo
    active.sort(key=lambda rule: rule.id)
    return active


def apply_rules(ctx: SafetyContext, rules: Iterable[ClinicalRule]) -> list[RuleMatch]:
    """Aplica las reglas activas al contexto. Determinista y ordenado."""
    matches: list[RuleMatch] = []
    for rule in rules:
        if rule_applies(rule, ctx):
            matches.append(
                RuleMatch(
                    rule_id=rule.id,
                    version=rule.version,
                    scope=rule.scope,
                    name=rule.name,
                    action=rule.action,
                    message=rule.message,
                    justification=rule.justification,
                    status=rule.status,
                    source_desc=rule.source_desc,
                )
            )
    return matches
