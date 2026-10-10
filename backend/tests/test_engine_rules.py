"""Pruebas del evaluador de reglas (app.engine.rules)."""
from __future__ import annotations

import json
from datetime import UTC

from sqlmodel import Session

from app.db import engine
from app.engine.rules import (
    SafetyContext,
    apply_rules,
    evaluate_condition,
    load_active_rules,
    rule_applies,
)
from app.models import ClinicalRule


def _rule(rule_id="T-R001", conditions=None, exceptions=None, action="advertir", status="candidate"):
    return ClinicalRule(
        id=rule_id,
        version=1,
        scope="test",
        name=f"regla {rule_id}",
        conditions=json.dumps(conditions or [{"type": "health_flag", "value": "embarazo"}]),
        exceptions=json.dumps(exceptions or []),
        action=action,
        message="mensaje",
        justification="justificacion",
        source_desc="fuente",
        status=status,
    )


class TestEvaluateCondition:
    def test_should_match_when_health_flag_present(self):
        ctx = SafetyContext(health_flags={"embarazo"})
        assert evaluate_condition({"type": "health_flag", "value": "embarazo"}, ctx)

    def test_should_not_match_when_health_flag_absent(self):
        ctx = SafetyContext()
        assert not evaluate_condition({"type": "health_flag", "value": "embarazo"}, ctx)

    def test_should_match_when_allergy_kind_confirmed(self):
        ctx = SafetyContext(allergies={"leche": ("alergia_confirmada", "alta")})
        assert evaluate_condition({"type": "allergy", "value": "leche"}, ctx)

    def test_should_not_match_when_allergy_is_intolerance(self):
        ctx = SafetyContext(allergies={"leche": ("intolerancia", "baja")})
        assert not evaluate_condition({"type": "allergy", "value": "leche"}, ctx)

    def test_should_match_when_dietary_pattern_equals(self):
        assert evaluate_condition({"type": "dietary_pattern", "value": "vegano"}, SafetyContext(dietary_pattern="vegano"))

    def test_should_match_when_onboarding_incomplete(self):
        assert evaluate_condition({"type": "no_onboarding", "value": True}, SafetyContext(onboarding_completed=False))
        assert not evaluate_condition({"type": "no_onboarding", "value": True}, SafetyContext(onboarding_completed=True))

    def test_should_return_false_when_unknown_condition_type(self):
        assert not evaluate_condition({"type": "inexistente", "value": 1}, SafetyContext())


class TestRuleApplies:
    def test_should_apply_when_all_conditions_met(self):
        rule = _rule(conditions=[{"type": "health_flag", "value": "embarazo"}])
        assert rule_applies(rule, SafetyContext(health_flags={"embarazo"}))

    def test_should_not_apply_when_any_condition_missing(self):
        rule = _rule(conditions=[
            {"type": "health_flag", "value": "embarazo"},
            {"type": "dietary_pattern", "value": "vegano"},
        ])
        ctx = SafetyContext(health_flags={"embarazo"}, dietary_pattern="omnivoro")
        assert not rule_applies(rule, ctx)

    def test_should_not_apply_when_exception_matches(self):
        rule = _rule(
            conditions=[{"type": "health_flag", "value": "embarazo"}],
            exceptions=[{"type": "dietary_pattern", "value": "vegano"}],
        )
        ctx = SafetyContext(health_flags={"embarazo"}, dietary_pattern="vegano")
        assert not rule_applies(rule, ctx)

    def test_should_not_apply_when_conditions_empty(self):
        assert not rule_applies(_rule(conditions=[]), SafetyContext())


class TestConfirmedAllergens:
    def test_should_include_only_confirmed_allergies(self):
        ctx = SafetyContext(allergies={
            "leche": ("alergia_confirmada", "alta"),
            "lactosa_simulada": ("intolerancia", "media"),
        })
        assert ctx.confirmed_allergens() == {"leche"}

    def test_should_include_only_severe_confirmed(self):
        ctx = SafetyContext(allergies={
            "leche": ("alergia_confirmada", "alta"),
            "huevo": ("alergia_confirmada", "baja"),
        })
        assert ctx.severe_allergens() == {"leche"}


class TestApplyRules:
    def test_should_return_matches_sorted_and_deterministic(self):
        rules = [_rule("T-A"), _rule("T-B", action="bloquear")]
        ctx = SafetyContext(health_flags={"embarazo"})
        first = [match.rule_id for match in apply_rules(ctx, rules)]
        second = [match.rule_id for match in apply_rules(ctx, rules)]
        assert first == second == ["T-A", "T-B"]

    def test_should_skip_rules_that_do_not_apply(self):
        rules = [_rule()]
        assert apply_rules(SafetyContext(), rules) == []


class TestLoadActiveRules:
    def test_should_load_approved_always_and_candidates_only_in_pilot(self):
        """Prueba con reglas dedicadas para no depender del estado global de otras pruebas."""
        from datetime import datetime



        with Session(engine) as session:
            if session.get(ClinicalRule, "ZZ-PILOT-CAND") is None:
                session.add(ClinicalRule(
                    id="ZZ-PILOT-CAND", version=1, scope="zz", name="cand",
                    conditions='[{"type": "health_flag", "value": "embarazo"}]',
                    exceptions="[]", action="advertir", message="m",
                    justification="j", source_desc="s", status="candidate",
                ))
            if session.get(ClinicalRule, "ZZ-PILOT-APR") is None:
                session.add(ClinicalRule(
                    id="ZZ-PILOT-APR", version=1, scope="zz", name="apr",
                    conditions='[{"type": "health_flag", "value": "embarazo"}]',
                    exceptions="[]", action="advertir", message="m",
                    justification="j", source_desc="s", status="approved",
                    reviewer="profesional@test.example", approved_at=datetime.now(UTC),
                ))
            session.commit()

            ids_pilot = {rule.id for rule in load_active_rules(session, pilot_mode=True)}
            ids_prod = {rule.id for rule in load_active_rules(session, pilot_mode=False)}

        assert "ZZ-PILOT-APR" in ids_pilot and "ZZ-PILOT-APR" in ids_prod
        assert "ZZ-PILOT-CAND" in ids_pilot  # candidata visible en modo piloto
        assert "ZZ-PILOT-CAND" not in ids_prod  # candidata NUNCA en produccion
