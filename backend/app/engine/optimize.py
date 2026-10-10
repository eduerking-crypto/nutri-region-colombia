"""Generador determinista de menus (prototipo v1 del optimizador, ADR-0010).

Estrategia greedy determinista: plantillas de comidas por grupos alimentarios
con rotacion estable por dia. No usa la IA ni aleatoriedad: mismas entradas ->
mismo menu. La eleccion final de libreria de optimizacion (OR-Tools u otra) se
decidira con un prototipo medible (ADR-0010); este modulo vive aislado detras
de esta interfaz.
"""
from __future__ import annotations

from dataclasses import dataclass

from app.engine.calc import scale, sum_nutrients
from app.models.catalog import Food, FoodNutrient

# Porciones nominales del proyecto (educativo, ajustable por el usuario en la UI)
NOMINAL_PORTIONS_GR = {
    "cereal": 75.0,
    "legumbre": 80.0,
    "vegetal": 150.0,
    "fruta": 150.0,
    "proteina_animal": 150.0,
    "lacteo": 240.0,
    "huevo": 100.0,
    "grasa": 12.0,
    "especia": 10.0,
}

# Plantillas de comidas por numero de comidas al dia
MEAL_TEMPLATES = {
    3: [
        ("desayuno", ["cereal", "lacteo", "fruta"]),
        ("almuerzo", ["cereal", "legumbre", "vegetal"]),
        ("cena", ["cereal", "vegetal", "proteina_animal"]),
    ],
    4: [
        ("desayuno", ["cereal", "lacteo", "fruta"]),
        ("almuerzo", ["cereal", "legumbre", "vegetal"]),
        ("onces", ["fruta", "cereal"]),
        ("cena", ["cereal", "vegetal", "proteina_animal"]),
    ],
    5: [
        ("desayuno", ["cereal", "lacteo", "fruta"]),
        ("media_manana", ["fruta"]),
        ("almuerzo", ["cereal", "legumbre", "vegetal"]),
        ("onces", ["fruta", "lacteo"]),
        ("cena", ["cereal", "vegetal", "proteina_animal"]),
    ],
}

# Grupos que se excluyen por patron alimentario
PATTERN_EXCLUSIONS = {
    "vegano": {"proteina_animal", "lacteo", "huevo"},
    "vegetariano": {"proteina_animal"},
}


@dataclass
class FoodEntry:
    """Composicion plana por alimento para el motor (determinista, sin ORM)."""

    food_id: str
    name: str
    food_group: str
    diet_tags: set[str]
    per_100g: dict[str, float]
    portion_g: float


def build_entries(foods: list[Food], nutrients: list[FoodNutrient]) -> list[FoodEntry]:
    """Convierte ORM en entradas planas del motor."""
    by_food: dict[str, dict[str, float]] = {}
    for nutrient in nutrients:
        by_food.setdefault(nutrient.food_id, {})[nutrient.nutrient] = nutrient.value
    entries = []
    for food in foods:
        per_100g = by_food.get(food.id, {})
        entries.append(
            FoodEntry(
                food_id=food.id,
                name=food.name_common,
                food_group=food.food_group,
                diet_tags=set(food.diet_tag_list),
                per_100g=per_100g,
                portion_g=NOMINAL_PORTIONS_GR.get(food.food_group, 100.0),
            )
        )
    return entries


def _filter_candidates(
    entries: list[FoodEntry],
    pattern: str,
    excluded_ids: set[str],
    rejected_ids: set[str],
) -> dict[str, list[FoodEntry]]:
    """Candidatas por grupo, priorizando preferencias. Orden estable."""
    banned_groups = PATTERN_EXCLUSIONS.get(pattern, set())
    candidates: dict[str, list[FoodEntry]] = {}
    for entry in entries:
        if entry.food_id in excluded_ids or entry.food_id in rejected_ids:
            continue
        if entry.food_group in banned_groups:
            continue
        candidates.setdefault(entry.food_group, []).append(entry)
    for group in candidates:
        candidates[group].sort(key=lambda e: e.food_id)
    return candidates


def generate_menu(
    entries: list[FoodEntry],
    days: int,
    meals_per_day: int,
    pattern: str,
    excluded_ids: set[str],
    preferred_ids: set[str],
    rejected_ids: set[str],
) -> tuple[dict, list[str]]:
    """Genera el menu. Devuelve (menu, warnings). Nunca inventa alimentos."""
    warnings: list[str] = []
    if meals_per_day not in MEAL_TEMPLATES:
        raise ValueError("meals_per_day debe estar entre 3 y 5")
    if not 1 <= days <= 7:
        raise ValueError("days debe estar entre 1 y 7")

    candidates = _filter_candidates(entries, pattern, excluded_ids, rejected_ids)
    # Priorizar preferidas dentro de cada grupo (orden estable: preferidas primero)
    for _group, group_entries in candidates.items():
        if preferred_ids:
            group_entries.sort(
                key=lambda e: (0 if e.food_id in preferred_ids else 1, e.food_id)
            )

    # Ajustar plantilla segun disponibilidad real
    template = MEAL_TEMPLATES[meals_per_day]
    adjusted: list[tuple[str, list[str]]] = []
    for meal_name, groups in template:
        usable = [g for g in groups if candidates.get(g)]
        missing = [g for g in groups if not candidates.get(g)]
        if missing:
            warnings.append(
                f"Sin alimentos del grupo '{', '.join(missing)}' para '{meal_name}': "
                "ese componente se omite (no se inventan alimentos)."
            )
        if usable:
            adjusted.append((meal_name, usable))

    menu_days = []
    counters: dict[str, int] = {}
    for day in range(1, days + 1):
        meals = []
        for meal_name, groups in adjusted:
            items = []
            for group in groups:
                pool = candidates[group]
                index = counters.get(group, 0)
                entry = pool[index % len(pool)]
                counters[group] = index + 1
                items.append(
                    {
                        "food_id": entry.food_id,
                        "name": entry.name,
                        "food_group": group,
                        "grams": entry.portion_g,
                    }
                )
            meals.append({"tipo": meal_name, "items": items})
        menu_days.append({"dia": day, "comidas": meals})

    menu = {
        "generator": "determinista-v1 (greedy con rotacion estable)",
        "porciones": "porciones nominales del proyecto (educativo, ajustable)",
        "dias": menu_days,
    }
    return menu, warnings


def menu_totals_per_day(menu: dict, entries: list[FoodEntry]) -> list[dict[str, float]]:
    """Totales nutricionales por dia (composicion de ingredientes crudos)."""
    lookup = {entry.food_id: entry for entry in entries}
    totals = []
    for day in menu.get("dias", []):
        scaled = []
        for meal in day["comidas"]:
            for item in meal["items"]:
                entry = lookup.get(item["food_id"])
                if entry and entry.per_100g:
                    scaled.append(scale(entry.per_100g, item["grams"]))
        totals.append(sum_nutrients(scaled))
    return totals


def shopping_list(menu: dict) -> dict[str, dict]:
    """Lista de compras consolidada por alimento (gramos totales)."""
    items: dict[str, dict] = {}
    for day in menu.get("dias", []):
        for meal in day["comidas"]:
            for item in meal["items"]:
                current = items.setdefault(
                    item["food_id"], {"name": item["name"], "grams": 0.0, "food_group": item["food_group"]}
                )
                current["grams"] += item["grams"]
    for current in items.values():
        current["grams"] = round(current["grams"], 1)
    return items


def substitutions_for(
    target: FoodEntry,
    entries: list[FoodEntry],
    excluded_ids: set[str],
    limit: int = 5,
) -> list[dict]:
    """Sustituciones del mismo grupo, ordenadas por similitud de composicion.

    Similitud simple: distancia euclidiana sobre macronutrientes clave.
    Determinista (mismo orden de entrada -> mismo orden de salida).
    """
    keys = ["proteina", "carbohidratos", "grasa_total", "fibra", "energia"]

    def distance(entry: FoodEntry) -> float:
        total = 0.0
        for key in keys:
            a = target.per_100g.get(key, 0.0)
            b = entry.per_100g.get(key, 0.0)
            total += (a - b) ** 2
        return total

    pool = [
        entry
        for entry in entries
        if entry.food_id != target.food_id
        and entry.food_id not in excluded_ids
        and entry.food_group == target.food_group
    ]
    pool.sort(key=lambda entry: (distance(entry), entry.food_id))
    result = []
    for entry in pool[:limit]:
        result.append(
            {
                "food_id": entry.food_id,
                "name": entry.name,
                "reason": (
                    f"Mismo grupo ('{target.food_group}') con composicion similar "
                    "(distancia euclidiana sobre macro y energia)."
                ),
                "distance": round(distance(entry), 2),
            }
        )
    return result
