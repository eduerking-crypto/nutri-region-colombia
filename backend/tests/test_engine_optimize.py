"""Pruebas del generador determinista de menus y sustituciones (optimize)."""
from __future__ import annotations

import pytest

from app.engine.optimize import (
    FoodEntry,
    build_entries,
    generate_menu,
    menu_totals_per_day,
    shopping_list,
    substitutions_for,
)


def _entry(food_id, group, kcal=100.0, prot=5.0, carb=10.0, fat=1.0, fiber=2.0, tags=None):
    return FoodEntry(
        food_id=food_id,
        name=f"Alimento {food_id}",
        food_group=group,
        diet_tags=tags or ({"animal"} if group in {"lacteo", "huevo", "proteina_animal"} else {"vegetal"}),
        per_100g={"energia": kcal, "proteina": prot, "carbohidratos": carb, "grasa_total": fat, "fibra": fiber},
        portion_g=100.0,
    )


def _full_catalog() -> list[FoodEntry]:
    return [
        _entry("A1", "cereal"),
        _entry("A2", "cereal"),
        _entry("B1", "legumbre"),
        _entry("V1", "vegetal"),
        _entry("V2", "vegetal"),
        _entry("F1", "fruta"),
        _entry("L1", "lacteo", tags={"animal"}),
        _entry("H1", "huevo", tags={"animal"}),
        _entry("P1", "proteina_animal", tags={"animal"}),
    ]


class TestGenerateMenu:
    def test_should_generate_all_days_when_full_catalog(self):
        menu, warnings = generate_menu(_full_catalog(), days=3, meals_per_day=3, pattern="omnivoro", excluded_ids=set(), preferred_ids=set(), rejected_ids=set())
        assert len(menu["dias"]) == 3
        assert warnings == []

    def test_should_be_deterministic_when_same_input_twice(self):
        args = (3, 3, "omnivoro", set(), set(), set())
        menu_one, _ = generate_menu(_full_catalog(), *args)
        menu_two, _ = generate_menu(_full_catalog(), *args)
        assert menu_one == menu_two

    def test_should_rotate_variety_across_days(self):
        menu, _ = generate_menu(_full_catalog(), days=2, meals_per_day=3, pattern="omnivoro", excluded_ids=set(), preferred_ids=set(), rejected_ids=set())
        day1_cereals = [item["food_id"] for meal in menu["dias"][0]["comidas"] for item in meal["items"] if item["food_group"] == "cereal"]
        day2_cereals = [item["food_id"] for meal in menu["dias"][1]["comidas"] for item in meal["items"] if item["food_group"] == "cereal"]
        assert day1_cereals != day2_cereals  # rotacion efectiva con 2 cereales

    def test_should_exclude_allergen_foods(self):
        menu, _ = generate_menu(_full_catalog(), days=1, meals_per_day=3, pattern="omnivoro", excluded_ids={"L1"}, preferred_ids=set(), rejected_ids=set())
        used = {item["food_id"] for day in menu["dias"] for meal in day["comidas"] for item in meal["items"]}
        assert "L1" not in used

    def test_should_exclude_vegan_forbidden_groups_when_pattern_vegano(self):
        menu, _ = generate_menu(_full_catalog(), days=1, meals_per_day=3, pattern="vegano", excluded_ids=set(), preferred_ids=set(), rejected_ids=set())
        used = {item["food_id"] for day in menu["dias"] for meal in day["comidas"] for item in meal["items"]}
        assert not (used & {"L1", "H1", "P1"})

    def test_should_prioritize_preferred_but_keep_determinism(self):
        menu, _ = generate_menu(_full_catalog(), days=1, meals_per_day=3, pattern="omnivoro", excluded_ids=set(), preferred_ids={"A2"}, rejected_ids=set())
        first_desayuno = menu["dias"][0]["comidas"][0]["items"]
        cereal_item = next(item for item in first_desayuno if item["food_group"] == "cereal")
        assert cereal_item["food_id"] == "A2"

    def test_should_exclude_rejected_foods(self):
        menu, _ = generate_menu(_full_catalog(), days=1, meals_per_day=3, pattern="omnivoro", excluded_ids=set(), preferred_ids=set(), rejected_ids={"A1"})
        used = {item["food_id"] for day in menu["dias"] for meal in day["comidas"] for item in meal["items"]}
        assert "A1" not in used

    def test_case4_should_warn_and_omit_when_group_missing(self):
        catalog = [entry for entry in _full_catalog() if entry.food_group != "proteina_animal"]
        menu, warnings = generate_menu(catalog, days=1, meals_per_day=3, pattern="omnivoro", excluded_ids=set(), preferred_ids=set(), rejected_ids=set())
        assert any("proteina_animal" in warning for warning in warnings)
        used_groups = {item["food_group"] for day in menu["dias"] for meal in day["comidas"] for item in meal["items"]}
        assert "proteina_animal" not in used_groups

    def test_should_raise_valueerror_when_meals_per_day_invalid(self):
        with pytest.raises(ValueError):
            generate_menu(_full_catalog(), days=1, meals_per_day=6, pattern="omnivoro", excluded_ids=set(), preferred_ids=set(), rejected_ids=set())

    def test_should_raise_valueerror_when_days_out_of_range(self):
        with pytest.raises(ValueError):
            generate_menu(_full_catalog(), days=8, meals_per_day=3, pattern="omnivoro", excluded_ids=set(), preferred_ids=set(), rejected_ids=set())


class TestMenuTotals:
    def test_should_sum_per_day_correctly(self):
        entries = _full_catalog()
        menu, _ = generate_menu(entries, days=1, meals_per_day=3, pattern="omnivoro", excluded_ids=set(), preferred_ids=set(), rejected_ids=set())
        totals = menu_totals_per_day(menu, entries)
        assert len(totals) == 1
        assert totals[0]["energia"] > 0

    def test_should_return_empty_when_menu_blocked(self):
        assert menu_totals_per_day({"dias": []}, []) == []


class TestShoppingList:
    def test_should_aggregate_grams_per_food(self):
        menu = {
            "dias": [
                {"dia": 1, "comidas": [{"tipo": "a", "items": [{"food_id": "A1", "name": "X", "food_group": "cereal", "grams": 100.0}, {"food_id": "A2", "name": "Y", "food_group": "cereal", "grams": 50.0}]}]},
                {"dia": 2, "comidas": [{"tipo": "a", "items": [{"food_id": "A1", "name": "X", "food_group": "cereal", "grams": 75.0}]}]},
            ]
        }
        result = shopping_list(menu)
        assert result["A1"]["grams"] == 175.0
        assert result["A2"]["grams"] == 50.0


class TestSubstitutions:
    def test_should_return_same_group_sorted_by_similarity(self):
        entries = _full_catalog()
        target = _entry("V1", "vegetal", kcal=100, prot=5, carb=10, fat=1, fiber=2)
        subs = substitutions_for(target, entries, excluded_ids=set())
        assert all(item["food_id"].startswith(("V2",)) for item in subs)
        assert subs[0]["reason"]

    def test_should_exclude_target_and_allergen_foods(self):
        entries = _full_catalog()
        target = entries[0]  # A1 cereal
        subs = substitutions_for(target, entries, excluded_ids={"A2"})
        assert "A2" not in {item["food_id"] for item in subs}
        assert "A1" not in {item["food_id"] for item in subs}

    def test_should_respect_limit(self):
        entries = [_entry(f"C{i}", "cereal") for i in range(20)]
        subs = substitutions_for(entries[0], entries, excluded_ids=set(), limit=5)
        assert len(subs) == 5


class TestBuildEntries:
    def test_should_map_nutrients_by_food(self):
        from sqlmodel import Session, select

        from app.db import engine
        from app.models import Food, FoodNutrient

        with Session(engine) as session:
            foods = session.exec(select(Food)).all()
            nutrients = session.exec(select(FoodNutrient)).all()
            entries = build_entries(foods, nutrients)
            assert entries
            yuca = next(entry for entry in entries if entry.food_id == "FDC-T-YUCA")
            assert yuca.per_100g["energia"] == 160.0
            assert yuca.portion_g == 150.0  # porcion nominal vegetal
