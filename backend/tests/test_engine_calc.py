"""Pruebas del modulo de calculo nutricional (app.engine.calc)."""
from __future__ import annotations

import pytest

from app.engine import calc


class TestScale:
    def test_should_scale_100g_to_100g_when_grams_is_100(self):
        values = {"energia": 365.0, "proteina": 7.1}
        assert calc.scale(values, 100) == {"energia": 365.0, "proteina": 7.1}

    def test_should_scale_linearly_when_grams_is_150(self):
        values = {"energia": 200.0}
        assert calc.scale(values, 150) == {"energia": 300.0}

    def test_should_return_zero_when_grams_is_0(self):
        assert calc.scale({"energia": 100.0}, 0) == {"energia": 0.0}

    def test_should_raise_valueerror_when_grams_negative(self):
        with pytest.raises(ValueError):
            calc.scale({"energia": 100.0}, -1)


class TestSum:
    def test_should_sum_same_keys_when_multiple_lists(self):
        result = calc.sum_nutrients([{"proteina": 10.0}, {"proteina": 5.0}])
        assert result == {"proteina": 15.0}

    def test_should_union_keys_when_lists_differ(self):
        result = calc.sum_nutrients([{"proteina": 1.0}, {"fibra": 2.0}])
        assert result == {"proteina": 1.0, "fibra": 2.0}

    def test_should_return_empty_dict_when_no_lists(self):
        assert calc.sum_nutrients([]) == {}


class TestEnergyFromMacros:
    def test_should_compute_atwater_when_typical_values(self):
        values = {"proteina": 10.0, "carbohidratos": 50.0, "grasa_total": 5.0}
        assert calc.energy_from_macros(values) == pytest.approx(10 * 4 + 50 * 4 + 5 * 9)

    def test_should_return_zero_when_macros_missing(self):
        assert calc.energy_from_macros({}) == 0.0


class TestMacroEnergyShare:
    def test_should_compute_shares_when_energy_positive(self):
        values = {"energia": 200.0, "carbohidratos": 30.0, "proteina": 10.0, "grasa_total": 4.0}
        shares = calc.macro_energy_share(values)
        assert shares["carbohidratos"] == pytest.approx(60.0)
        assert shares["proteina"] == pytest.approx(20.0)
        assert shares["grasa"] == pytest.approx(18.0)

    def test_should_return_none_when_energy_is_zero(self):
        shares = calc.macro_energy_share({"energia": 0.0, "proteina": 3.0})
        assert shares == {"carbohidratos": None, "proteina": None, "grasa": None}

    def test_should_return_none_when_energy_missing(self):
        assert calc.macro_energy_share({"proteina": 3.0})["proteina"] is None


class TestAdequacy:
    def test_should_flag_in_range_when_shares_within_reference(self):
        values = {"energia": 500.0, "carbohidratos": 80.0, "proteina": 15.0, "grasa_total": 8.0}
        result = {item["metric"]: item for item in calc.adequacy(values)}
        assert result["carbohidratos"]["in_range"] is True
        assert result["proteina"]["in_range"] is True
        assert result["grasa"]["in_range"] is False  # 8g*9/500 = 14.4% < 15%

    def test_should_return_none_when_no_energy(self):
        for item in calc.adequacy({"energia": 0.0}):
            assert item["value"] is None
            assert item["in_range"] is None

    def test_should_expose_source_and_trust_tier(self):
        result = calc.adequacy({"energia": 400.0, "carbohidratos": 60.0})
        assert all(item["trust_tier"] == "literatura" for item in result)
        assert all("OMS/FAO TRS 916" in item["source"] for item in result)
        assert all(item["verification_status"] == "unverified" for item in result)


class TestRecipeNutrition:
    def test_should_divide_by_servings_when_multiple_ingredients(self):
        ingredient_a = ({"energia": 100.0}, 200.0)  # 200 kcal
        ingredient_b = ({"energia": 50.0}, 100.0)  # 50 kcal
        per_serving = calc.recipe_nutrition([ingredient_a, ingredient_b], servings=4)
        assert per_serving["energia"] == pytest.approx(62.5)

    def test_should_raise_valueerror_when_servings_below_1(self):
        with pytest.raises(ValueError):
            calc.recipe_nutrition([({"energia": 1.0}, 10.0)], servings=0)
