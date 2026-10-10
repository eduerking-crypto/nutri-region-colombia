"""Modelos del catalogo cientifico publico.

Convenciones (ver docs/data-model.md):
- Composicion por 100 g de porcion comestible.
- Listas serializadas como JSON-texto para portabilidad SQLite <-> PostgreSQL.
- Todo dato cientifico lleva procedencia: trust_tier + source + retrieved_at.

NOTA: no usar `from __future__ import annotations` en este archivo: rompe la
resolucion de anotaciones de SQLModel/SQLAlchemy.
"""
import json
from datetime import date

from sqlmodel import Field, SQLModel


def jloads(raw: str | None) -> list:
    if not raw:
        return []
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return []


def jdumps(value: list) -> str:
    return json.dumps(value, ensure_ascii=False)


class Source(SQLModel, table=True):
    __tablename__ = "sources"

    id: str = Field(primary_key=True)
    name: str
    kind: str
    version: str
    license: str
    redistribution_allowed: bool = True
    access_method: str
    url: str | None = None
    citation: str | None = None
    retrieved_at: date
    notes: str | None = None


class Food(SQLModel, table=True):
    __tablename__ = "foods"

    id: str = Field(primary_key=True)
    name_common: str
    name_variants: str = "[]"
    name_scientific: str | None = None
    food_group: str
    state: str
    edible_portion_pct: float | None = None
    region_associations: str = "[]"
    external_ids: str = "[]"
    allergens: str = "[]"
    diet_tags: str = "[]"
    trust_tier: str = "medido"
    source_id: str = Field(foreign_key="sources.id")
    source_version: str
    retrieved_at: date
    verification_status: str = "unverified"
    notes: str | None = None

    @property
    def region_list(self) -> list[str]:
        return jloads(self.region_associations)

    @property
    def allergen_list(self) -> list[str]:
        return jloads(self.allergens)

    @property
    def diet_tag_list(self) -> list[str]:
        return jloads(self.diet_tags)


class FoodNutrient(SQLModel, table=True):
    __tablename__ = "food_nutrients"

    id: int | None = Field(default=None, primary_key=True)
    food_id: str = Field(foreign_key="foods.id", index=True)
    nutrient: str = Field(index=True)
    value: float
    unit: str
    basis: str = "100 g de porcion comestible"
    method: str | None = None
    trust_tier: str
    source_id: str = Field(foreign_key="sources.id")
    retrieved_at: date
    verification_status: str = "unverified"
    uncertainty_notes: str | None = None


class PriceObservation(SQLModel, table=True):
    __tablename__ = "price_observations"

    id: int | None = Field(default=None, primary_key=True)
    food_id: str = Field(foreign_key="foods.id", index=True)
    product_desc: str
    municipality: str = Field(index=True)
    market: str | None = None
    commercial_unit: str
    price_cop: float
    observed_at: date = Field(index=True)
    data_type: str = "observado"
    source_desc: str
    confidence: str | None = None
    method: str | None = None
    created_by: int | None = None


class Recipe(SQLModel, table=True):
    __tablename__ = "recipes"

    id: str = Field(primary_key=True)
    name: str
    variant_name: str | None = None
    region: str | None = None
    origin_notes: str | None = None
    servings: int
    time_minutes: int | None = None
    equipment: str = "[]"
    steps: str = "[]"
    yield_notes: str | None = None
    nutrition_method: str | None = None
    trust_tier: str = "educativo"
    source_desc: str
    retrieved_at: date
    verification_status: str = "unverified"

    @property
    def steps_list(self) -> list[str]:
        return jloads(self.steps)


class RecipeIngredient(SQLModel, table=True):
    __tablename__ = "recipe_ingredients"

    id: int | None = Field(default=None, primary_key=True)
    recipe_id: str = Field(foreign_key="recipes.id", index=True)
    food_id: str = Field(foreign_key="foods.id")
    quantity_g: float
    unit_note: str | None = None


class Evidence(SQLModel, table=True):
    __tablename__ = "evidence"

    id: str = Field(primary_key=True)
    title: str
    citation: str
    doi: str | None = None
    pmid: str | None = None
    stable_url: str | None = None
    study_type: str | None = None
    population: str | None = None
    relevant_finding: str | None = None
    limitations: str | None = None
    trust_tier: str = "literatura"
    reviewed_at: date
    verification_status: str = "unverified"
    links: str = "[]"
    notes: str | None = None
