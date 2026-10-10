"""Pruebas de propiedad del motor (determinismo, linealidad, consistencia)."""
from __future__ import annotations

from hypothesis import given, settings
from hypothesis import strategies as st

from app.engine.calc import energy_from_macros, macro_energy_share, scale, sum_nutrients
from app.engine.optimize import FoodEntry, generate_menu

floats = st.floats(min_value=0, max_value=900, allow_nan=False, allow_infinity=False)


@given(grams=st.floats(min_value=0, max_value=10_000), value=floats)
def test_scale_should_be_linear_when_any_grams(value, grams):
    half = scale({"x": value}, grams / 2) if grams > 0 else {"x": 0.0}
    full = scale({"x": value}, grams)
    assert full["x"] == pytest_approx(half["x"] * 2)


@given(
    a=st.floats(min_value=0, max_value=500, allow_nan=False),
    b=st.floats(min_value=0, max_value=500, allow_nan=False),
)
def test_sum_should_be_commutative_when_two_lists(a, b):
    one_way = sum_nutrients([{"k": a}, {"k": b}])
    other_way = sum_nutrients([{"k": b}, {"k": a}])
    assert one_way == other_way


@given(prot=floats, carb=floats, fat=floats)
def test_energy_from_macros_should_be_non_negative(prot, carb, fat):
    assert energy_from_macros({"proteina": prot, "carbohidratos": carb, "grasa_total": fat}) >= 0


@given(carb=floats, prot=floats, fat=floats)
def test_macro_shares_should_sum_100_when_energy_consistent(carb, prot, fat):
    """Cuando la energia declarada coincide con la de los macros, las participaciones suman 100 %."""
    macros = {"carbohidratos": carb, "proteina": prot, "grasa_total": fat}
    energia = energy_from_macros(macros)
    if energia > 0:
        shares = macro_energy_share({**macros, "energia": energia})
        assert abs(sum(shares.values()) - 100.0) < 0.01


@settings(max_examples=25, deadline=None)
@given(seed=st.integers(min_value=0, max_value=100))
def test_menu_generation_should_be_deterministic_for_same_input(seed):
    entries = [
        FoodEntry(food_id=f"F{i}", name=f"f{i}", food_group=g, diet_tags=set(),
                  per_100g={"energia": 50.0, "proteina": 2.0}, portion_g=100.0)
        for i, g in enumerate(["cereal", "legumbre", "vegetal", "fruta", "lacteo",
                               "huevo", "proteina_animal", "vegetal", "cereal"])
    ]
    args = dict(days=3, meals_per_day=3, pattern="omnivoro",
                excluded_ids=set(), preferred_ids=set(), rejected_ids=set())
    menu_one, _ = generate_menu(entries, **args)
    menu_two, _ = generate_menu(entries, **args)
    assert menu_one == menu_two


def pytest_approx(value, rel=1e-6):
    class _Approx:
        def __eq__(self, other):
            return abs(other - value) <= rel * max(abs(other), abs(value), 1.0)
    return _Approx()
