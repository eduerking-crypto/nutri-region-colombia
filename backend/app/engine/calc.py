"""Calculo nutricional reproducible (base 100 g de porcion comestible).

Rangos de referencia de distribucion de macronutrientes:
OMS/FAO, Informe Tecnico 916 (2003) — diet, nutrition and the prevention of
chronic diseases. Cita marcada trust_tier=literatura, verification=unverified
hasta verificacion profesional (ver data/rules y pending-decisions.md).
"""
from __future__ import annotations

from collections.abc import Iterable, Mapping

# Distribucion de energia por macronutriente (rango, % de energia total).
# Fuente declarada: OMS/FAO TRS 916 (2003). Estado: pendiente de verificacion.
REFERENCE_RANGES = {
    "carbohidratos": {"min": 55.0, "max": 75.0, "unit": "% energia", "source": "OMS/FAO TRS 916 (2003)"},
    "proteina": {"min": 10.0, "max": 15.0, "unit": "% energia", "source": "OMS/FAO TRS 916 (2003)"},
    "grasa": {"min": 15.0, "max": 30.0, "unit": "% energia", "source": "OMS/FAO TRS 916 (2003)"},
}
REFERENCE_TRUST_TIER = "literatura"
REFERENCE_VERIFICATION = "unverified"

ATWATER = {"proteina": 4.0, "carbohidratos": 4.0, "grasa_total": 9.0}

# Nutrientes clave usados por el motor (clave canonica del proyecto)
KEY_NUTRIENTS = [
    "energia",
    "proteina",
    "grasa_total",
    "carbohidratos",
    "fibra",
    "azucares",
    "calcio",
    "hierro",
    "potasio",
    "sodio",
    "vitamina_c",
    "folato",
]


def scale(per_100g: Mapping[str, float], grams: float) -> dict[str, float]:
    """Escala una composicion por 100 g a una cantidad en gramos."""
    if grams < 0:
        raise ValueError("grams debe ser >= 0")
    return {key: value * grams / 100.0 for key, value in per_100g.items()}


def sum_nutrients(lists: Iterable[Mapping[str, float]]) -> dict[str, float]:
    """Suma varias composiciones (claves union)."""
    totals: dict[str, float] = {}
    for one in lists:
        for key, value in one.items():
            totals[key] = totals.get(key, 0.0) + value
    return totals


def energy_from_macros(values: Mapping[str, float]) -> float:
    """Energia estimada por factores generales de Atwater (kcal)."""
    return (
        values.get("proteina", 0.0) * ATWATER["proteina"]
        + values.get("carbohidratos", 0.0) * ATWATER["carbohidratos"]
        + values.get("grasa_total", 0.0) * ATWATER["grasa_total"]
    )


def macro_energy_share(values: Mapping[str, float]) -> dict[str, float | None]:
    """Porcentaje de energia (kcal) aportada por cada macronutriente.

    Devuelve None cuando no hay energia para evitar division por cero;
    el llamador debe tratarlo como 'sin datos', nunca como 0 %.
    """
    kcal = values.get("energia", 0.0)
    if kcal is None or kcal <= 0:
        return {"carbohidratos": None, "proteina": None, "grasa": None}
    return {
        "carbohidratos": values.get("carbohidratos", 0.0) * 4.0 * 100.0 / kcal,
        "proteina": values.get("proteina", 0.0) * 4.0 * 100.0 / kcal,
        "grasa": values.get("grasa_total", 0.0) * 9.0 * 100.0 / kcal,
    }


def adequacy(values_per_day: Mapping[str, float]) -> list[dict]:
    """Evalua la distribucion de macronutrientes contra los rangos de referencia.

    'in_range: null' significa sin datos suficientes para evaluar (energia 0).
    """
    shares = macro_energy_share(values_per_day)
    result: list[dict] = []
    labels = {"carbohidratos": "Carbohidratos", "proteina": "Proteina", "grasa": "Grasa"}
    for key, label in labels.items():
        reference = REFERENCE_RANGES[key]
        share = shares[key if key != "grasa" else "grasa"]
        result.append(
            {
                "metric": key,
                "label": label,
                "value": round(share, 1) if share is not None else None,
                "unit": reference["unit"],
                "range": [reference["min"], reference["max"]],
                "in_range": (
                    None
                    if share is None
                    else reference["min"] <= share <= reference["max"]
                ),
                "source": reference["source"],
                "trust_tier": REFERENCE_TRUST_TIER,
                "verification_status": REFERENCE_VERIFICATION,
            }
        )
    return result


def recipe_nutrition(
    ingredients: Iterable[tuple[Mapping[str, float], float]],
    servings: int,
) -> dict[str, float]:
    """Nutricion por porcion de una receta a partir de sus ingredientes.

    ingredients: pares (composicion por 100 g, gramos del ingrediente).
    Limitacion declarada en la UI: composicion de ingredientes crudos; los
    cambios por coccion no estan incluidos salvo en los datos de origen.
    """
    if servings < 1:
        raise ValueError("servings debe ser >= 1")
    scaled = [scale(per_100g, grams) for per_100g, grams in ingredients]
    total = sum_nutrients(scaled)
    return {key: value / servings for key, value in total.items()}
