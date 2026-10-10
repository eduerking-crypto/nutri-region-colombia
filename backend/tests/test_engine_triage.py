"""Pruebas del triage de seguridad — catalogo adverso del plan de pruebas (casos 1-14)."""
from __future__ import annotations

from test_engine_rules import _rule

from app.engine.rules import SafetyContext
from app.engine.triage import build_context, evaluate_safety, food_allergy_conflicts
from app.models.catalog import Food
from app.models.user import UserAllergy, UserHealthFlag, UserProfile


def _food(food_id="FDC-T-LECHE", allergens=("leche",)) -> Food:
    return Food(
        id=food_id,
        name_common="Alimento",
        food_group="lacteo",
        state="crudo",
        allergens='["' + '","'.join(allergens) + '"]' if allergens else "[]",
        trust_tier="medido",
        source_id="SRC-TEST",
        source_version="t",
        retrieved_at=__import__("datetime").date(2026, 1, 1),
    )


def _ctx(**kwargs) -> SafetyContext:
    defaults = {"onboarding_completed": True}
    defaults.update(kwargs)
    return SafetyContext(**defaults)


class TestBase:
    def test_should_be_ok_when_context_clean(self):
        result = evaluate_safety(_ctx(), rules=[])
        assert result.status == "ok"
        assert result.messages == []

    def test_should_warn_when_onboarding_incomplete(self):
        result = evaluate_safety(SafetyContext(), rules=[])
        assert result.status == "advertencia"
        assert any(msg.code == "perfil_incompleto" for msg in result.messages)

    def test_should_be_deterministic_when_same_input_twice(self):
        ctx = _ctx(health_flags={"diabetes_medicamentos"}, allergies={"leche": ("alergia_confirmada", "alta")})
        rules = [_rule("T-DIAB", action="derivar_profesional")]
        first = evaluate_safety(ctx, rules)
        second = evaluate_safety(ctx, rules)
        assert first.status == second.status
        assert [m.code for m in first.messages] == [m.code for m in second.messages]
        assert first.applied_rules == second.applied_rules


class TestAlergias:
    def test_case1_should_exclude_allergen_foods_and_warn_when_allergy_confirmed(self):
        ctx = _ctx(allergies={"leche": ("alergia_confirmada", "media")})
        foods = [_food("F1", ("leche",)), _food("F2", ())]
        result = evaluate_safety(ctx, rules=[], available_foods=foods)
        assert "F1" in result.excluded_food_ids
        assert "F2" not in result.excluded_food_ids
        assert result.status == "advertencia"
        assert "DESIGN-ALERGENOS v1" in result.applied_rules

    def test_case1b_should_never_claim_safe_substitution_when_severe_allergy(self):
        ctx = _ctx(allergies={"leche": ("alergia_confirmada", "alta")})
        result = evaluate_safety(ctx, rules=[])
        message = " ".join(msg.message for msg in result.messages)
        assert "contaminacion cruzada" in message

    def test_should_not_exclude_when_intolerance_only(self):
        ctx = _ctx(allergies={"leche": ("intolerancia", "media")})
        foods = [_food("F1", ("leche",))]
        result = evaluate_safety(ctx, rules=[], available_foods=foods)
        assert "F1" not in result.excluded_food_ids  # no es exclusion dura, se advierte en UI

    def test_conflicts_should_list_user_allergen_overlap(self):
        ctx = _ctx(allergies={"leche": ("alergia_confirmada", "alta")})
        conflicts = food_allergy_conflicts(_food(), ctx)
        assert conflicts == [{"allergen": "leche", "kind": "alergia_confirmada", "severity": "alta"}]


class TestUrgencia:
    def test_case11_should_return_urgencia_when_alarm_symptoms(self):
        ctx = _ctx(health_flags={"sintomas_alarma"})
        result = evaluate_safety(ctx, rules=[])
        assert result.status == "urgencia"
        assert any(msg.code == "sintomas_alarma" for msg in result.messages)

    def test_case11b_urgencia_wins_over_everything_else(self):
        ctx = _ctx(
            health_flags={"sintomas_alarma", "diabetes_medicamentos"},
            allergies={"leche": ("alergia_confirmada", "alta")},
        )
        rules = [_rule("T-DIAB", action="derivar_profesional")]
        result = evaluate_safety(ctx, rules)
        assert result.status == "urgencia"


class TestDerivacionProfesional:
    def test_case5_diabetes_meds_should_require_professional(self):
        ctx = _ctx(health_flags={"diabetes_medicamentos"})
        rules = [_rule("T-DIAB", conditions=[{"type": "health_flag", "value": "diabetes_medicamentos"}], action="derivar_profesional")]
        result = evaluate_safety(ctx, rules)
        assert result.status == "requiere_profesional"
        assert "T-DIAB v1" in result.applied_rules

    def test_case2_renal_should_require_professional(self):
        ctx = _ctx(health_flags={"enfermedad_renal"})
        rules = [_rule("T-RENAL", conditions=[{"type": "health_flag", "value": "enfermedad_renal"}], action="derivar_profesional")]
        result = evaluate_safety(ctx, rules)
        assert result.status == "requiere_profesional"

    def test_case6_pregnancy_should_require_professional(self):
        ctx = _ctx(health_flags={"embarazo"})
        rules = [_rule("T-EMB", action="derivar_profesional", status="approved")]
        result = evaluate_safety(ctx, rules)
        assert result.status == "requiere_profesional"

    def test_case8_tca_signals_should_require_professional_with_caring_message(self):
        ctx = _ctx(health_flags={"posible_tca"})
        rules = [_rule("T-TCA", conditions=[{"type": "health_flag", "value": "posible_tca"}], action="derivar_profesional")]
        result = evaluate_safety(ctx, rules)
        assert result.status == "requiere_profesional"

    def test_case9_involuntary_weight_loss_should_require_professional(self):
        ctx = _ctx(health_flags={"perdida_peso_involuntaria"})
        rules = [_rule("T-DESNUT", conditions=[{"type": "health_flag", "value": "perdida_peso_involuntaria"}], action="derivar_profesional")]
        result = evaluate_safety(ctx, rules)
        assert result.status == "requiere_profesional"

    def test_lactancia_should_only_warn(self):
        ctx = _ctx(health_flags={"lactancia"})
        rules = [_rule("T-LACT", conditions=[{"type": "health_flag", "value": "lactancia"}], action="advertir")]
        result = evaluate_safety(ctx, rules)
        assert result.status == "advertencia"

    def test_case12_candidate_rule_should_not_apply_without_pilot(self):
        """El llamador filtra candidatas fuera de piloto; el triage aplica lo que recibe.
        Esta prueba documenta que una regla candidata NO llega al triage en produccion."""
        ctx = _ctx(health_flags={"diabetes_medicamentos"})
        result = evaluate_safety(ctx, rules=[])  # produccion: solo approved llegan aqui
        assert result.status == "ok"
        assert "T-DIAB" not in " ".join(result.applied_rules)


class TestConflictos:
    def test_case2b_multiple_conditions_should_escalate_to_max_severity(self):
        ctx = _ctx(health_flags={"diabetes_medicamentos", "embarazo"})
        rules = [
            _rule("T-DIAB", action="derivar_profesional"),
            _rule("T-EMB", action="derivar_profesional"),
        ]
        result = evaluate_safety(ctx, rules)
        assert result.status == "requiere_profesional"
        assert len([rule for rule in result.applied_rules if "T-" in rule]) == 2


class TestBuildContext:
    def test_should_map_profile_allergies_and_flags(self):
        profile = UserProfile(
            user_id=1,
            municipality="Bogota",
            dietary_pattern="vegano",
            onboarding_completed=True,
        )
        allergies = [UserAllergy(id=1, user_id=1, allergen="huevo", kind="alergia_confirmada", severity="alta")]
        flags = [UserHealthFlag(id=1, user_id=1, flag="lactancia")]
        ctx = build_context(profile, allergies, flags)
        assert ctx.dietary_pattern == "vegano"
        assert ctx.municipality == "Bogota"
        assert ctx.allergies["huevo"] == ("alergia_confirmada", "alta")
        assert "lactancia" in ctx.health_flags
        assert ctx.onboarding_completed is True

    def test_should_default_onboarding_false_when_profile_none(self):
        ctx = build_context(None, [], [])
        assert ctx.onboarding_completed is False
        assert ctx.dietary_pattern == "omnivoro"
