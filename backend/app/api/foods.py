"""Catalogo publico: alimentos, fichas, recetas y sustituciones."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query
from sqlmodel import select

from app.api.deps import OptionalUser, SessionDep
from app.engine.optimize import (
    build_entries,
    substitutions_for,
)
from app.engine.triage import build_context, food_allergy_conflicts
from app.models import (
    Food,
    FoodNutrient,
    Recipe,
    RecipeIngredient,
    Source,
    UserAllergy,
    UserHealthFlag,
    UserProfile,
)
from app.models.catalog import jloads
from app.schemas import FoodDetailOut, FoodOut, RecipeOut

router = APIRouter(prefix="/alimentos", tags=["alimentos"])

# Nutrientes a mostrar en listados (claves del proyecto)
LIST_NUTRIENTS = {"energia", "proteina"}


@router.get("", response_model=list[FoodOut])
def listar_alimentos(
    session: SessionDep,
    search: str | None = None,
    food_group: str | None = None,
    region: str | None = None,
    limit: int = Query(default=100, ge=1, le=500),
) -> list[FoodOut]:
    """Listado publico. Exclusion de alergenos solo cuando hay sesion."""
    foods = session.exec(select(Food)).all()
    nutrients = session.exec(select(FoodNutrient)).all()
    per_food: dict[str, dict[str, float]] = {}
    for nutrient in nutrients:
        per_food.setdefault(nutrient.food_id, {})[nutrient.nutrient] = nutrient.value

    result = []
    for food in sorted(foods, key=lambda f: f.name_common):
        if search and search.lower() not in food.name_common.lower():
            continue
        if food_group and food.food_group != food_group:
            continue
        if region and region not in food.region_list:
            continue
        values = per_food.get(food.id, {})
        result.append(
            FoodOut(
                id=food.id,
                name_common=food.name_common,
                name_variants=jloads(food.name_variants),
                name_scientific=food.name_scientific,
                food_group=food.food_group,
                state=food.state,
                region_associations=food.region_list,
                allergens=food.allergen_list,
                trust_tier=food.trust_tier,
                source_id=food.source_id,
                retrieved_at=food.retrieved_at,
                verification_status=food.verification_status,
                notes=food.notes,
                energia_kcal=values.get("energia"),
                proteina_g=values.get("proteina"),
            )
        )
    return result[:limit]


@router.get("/grupos")
def grupos(session: SessionDep) -> list[dict]:
    foods = session.exec(select(Food)).all()
    counts: dict[str, int] = {}
    for food in foods:
        counts[food.food_group] = counts.get(food.food_group, 0) + 1
    return [{"group": group, "total": total} for group, total in sorted(counts.items())]


@router.get("/{food_id}", response_model=FoodDetailOut)
def ficha_alimento(food_id: str, session: SessionDep, user: OptionalUser = None) -> FoodDetailOut:
    food = session.get(Food, food_id)
    if food is None:
        raise HTTPException(status_code=404, detail="Alimento no encontrado.")
    nutrients = session.exec(
        select(FoodNutrient).where(FoodNutrient.food_id == food_id)
    ).all()
    source = session.get(Source, food.source_id)

    conflicts: list[dict] = []
    if user is not None:
        profile = session.exec(
            select(UserProfile).where(UserProfile.user_id == user.id)
        ).first()
        allergies = session.exec(select(UserAllergy).where(UserAllergy.user_id == user.id)).all()
        flags = session.exec(select(UserHealthFlag).where(UserHealthFlag.user_id == user.id)).all()
        ctx = build_context(profile, allergies, flags)
        conflicts = food_allergy_conflicts(food, ctx)

    detail = FoodDetailOut(
        id=food.id,
        name_common=food.name_common,
        name_variants=jloads(food.name_variants),
        name_scientific=food.name_scientific,
        food_group=food.food_group,
        state=food.state,
        region_associations=food.region_list,
        allergens=food.allergen_list,
        trust_tier=food.trust_tier,
        source_id=food.source_id,
        retrieved_at=food.retrieved_at,
        verification_status=food.verification_status,
        notes=food.notes,
        energia_kcal=None,
        proteina_g=None,
        nutrients=[
            {
                "nutrient": nutrient.nutrient,
                "value": nutrient.value,
                "unit": nutrient.unit,
                "basis": nutrient.basis,
                "method": nutrient.method,
                "trust_tier": nutrient.trust_tier,
                "verification_status": nutrient.verification_status,
            }
            for nutrient in sorted(nutrients, key=lambda n: n.nutrient)
        ],
        source_citation=source.citation if source else None,
        allergy_conflicts=conflicts,
    )
    if nutrients:
        values = {nutrient.nutrient: nutrient.value for nutrient in nutrients}
        detail.energia_kcal = values.get("energia")
        detail.proteina_g = values.get("proteina")
    return detail


@router.get("/{food_id}/sustituciones")
def sustituciones(food_id: str, session: SessionDep, user: OptionalUser = None) -> dict:
    target_food = session.get(Food, food_id)
    if target_food is None:
        raise HTTPException(status_code=404, detail="Alimento no encontrado.")
    foods = session.exec(select(Food)).all()
    nutrients = session.exec(select(FoodNutrient)).all()
    entries = build_entries(foods, nutrients)

    excluded: set[str] = set()
    user_ctx = None
    if user is not None:
        profile = session.exec(
            select(UserProfile).where(UserProfile.user_id == user.id)
        ).first()
        allergies = session.exec(select(UserAllergy).where(UserAllergy.user_id == user.id)).all()
        flags = session.exec(select(UserHealthFlag).where(UserHealthFlag.user_id == user.id)).all()
        user_ctx = build_context(profile, allergies, flags)
        excluded = set()
        for food in foods:
            if set(food.allergen_list) & user_ctx.confirmed_allergens():
                excluded.add(food.id)

    target = next((entry for entry in entries if entry.food_id == food_id), None)
    if target is None:
        raise HTTPException(status_code=404, detail="Alimento sin datos de composicion.")
    subs = substitutions_for(target, entries, excluded)
    return {
        "target": {"food_id": target.food_id, "name": target.name, "food_group": target.food_group},
        "sustituciones": subs,
        "aviso": (
            "Sustituciones por composicion y grupo alimentario. Verifica siempre "
            "ingredientes y contaminacion cruzada si tienes alergias."
        ),
    }


@router.get("/recetas/todas", response_model=list[RecipeOut])
def recetas(session: SessionDep) -> list[RecipeOut]:
    recipes = session.exec(select(Recipe)).all()
    ingredients = session.exec(select(RecipeIngredient)).all()
    foods = {food.id: food for food in session.exec(select(Food)).all()}
    nutrients = session.exec(select(FoodNutrient)).all()
    per_food: dict[str, dict[str, float]] = {}
    for nutrient in nutrients:
        per_food.setdefault(nutrient.food_id, {})[nutrient.nutrient] = nutrient.value

    result = []
    for recipe in sorted(recipes, key=lambda r: r.name):
        recipe_ings = [item for item in ingredients if item.recipe_id == recipe.id]
        ingredient_payload = []
        nutrition_pairs = []
        for item in recipe_ings:
            food = foods.get(item.food_id)
            if food is None:
                continue
            ingredient_payload.append(
                {
                    "food_id": item.food_id,
                    "name": food.name_common,
                    "grams": item.quantity_g,
                    "unit_note": item.unit_note,
                }
            )
            if item.food_id in per_food:
                nutrition_pairs.append((per_food[item.food_id], item.quantity_g))
        nutrition = None
        if nutrition_pairs and recipe.servings:
            scaled = []
            for per_100g, grams in nutrition_pairs:
                scaled.append({k: v * grams / 100.0 for k, v in per_100g.items()})
            totals: dict[str, float] = {}
            for one in scaled:
                for key, value in one.items():
                    totals[key] = totals.get(key, 0.0) + value
            nutrition = {
                key: round(value / recipe.servings, 2) for key, value in totals.items()
            }
        result.append(
            RecipeOut(
                id=recipe.id,
                name=recipe.name,
                variant_name=recipe.variant_name,
                region=recipe.region,
                servings=recipe.servings,
                time_minutes=recipe.time_minutes,
                steps=recipe.steps_list,
                trust_tier=recipe.trust_tier,
                source_desc=recipe.source_desc,
                nutrition_method=recipe.nutrition_method,
                ingredients=ingredient_payload,
                nutrition_per_serving=nutrition,
            )
        )
    return result


@router.get("/recetas/{recipe_id}", response_model=RecipeOut)
def receta_detalle(recipe_id: str, session: SessionDep) -> RecipeOut:
    all_recipes = recetas(session=session)
    for recipe in all_recipes:
        if recipe.id == recipe_id:
            return recipe
    raise HTTPException(status_code=404, detail="Receta no encontrada.")
