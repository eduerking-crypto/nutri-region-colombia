"""Esquemas Pydantic de entrada/salida (contrato OpenAPI)."""
from __future__ import annotations

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, EmailStr, Field

TrustTier = Literal["medido", "estimado", "literatura", "educativo"]
VerificationStatus = Literal["unverified", "verified", "rejected"]


# --- Auth ---
class RegistroIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    display_name: str | None = None
    accept_consent: bool = Field(description="Consentimiento informado obligatorio")


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    display_name: str | None


class UserOut(BaseModel):
    id: int
    email: EmailStr
    role: str
    display_name: str | None
    consent_version: str | None
    consent_at: datetime | None
    created_at: datetime


# --- Perfil ---
class ProfileIn(BaseModel):
    department: str | None = None
    municipality: str | None = None
    zone: Literal["urbana", "rural"] | None = None
    household_size: int = Field(default=1, ge=1, le=20)
    budget_weekly_cop: float | None = Field(default=None, ge=0)
    cooking_time_minutes: int | None = Field(default=None, ge=0, le=600)
    has_refrigeration: bool = True
    meals_per_day: int = Field(default=3, ge=1, le=6)
    dietary_pattern: Literal["omnivoro", "vegetariano", "vegano"] = "omnivoro"
    preferred_foods: list[str] = []
    rejected_foods: list[str] = []
    onboarding_completed: bool = False


class ProfileOut(ProfileIn):
    user_id: int


class AllergyIn(BaseModel):
    allergen: str
    kind: Literal["alergia_confirmada", "intolerancia", "reaccion_conocida"] = "alergia_confirmada"
    severity: Literal["alta", "media", "baja", "desconocida"] = "desconocida"
    notes: str | None = None


class AllergyOut(AllergyIn):
    id: int


class HealthFlagIn(BaseModel):
    flag: Literal[
        "diabetes_medicamentos",
        "enfermedad_renal",
        "embarazo",
        "lactancia",
        "posible_tca",
        "perdida_peso_involuntaria",
        "sintomas_alarma",
    ]
    self_reported: bool = True
    notes: str | None = None


class HealthFlagOut(HealthFlagIn):
    id: int


# --- Catalogo ---
class NutrientOut(BaseModel):
    nutrient: str
    value: float
    unit: str
    basis: str
    method: str | None
    trust_tier: TrustTier
    verification_status: VerificationStatus


class FoodOut(BaseModel):
    id: str
    name_common: str
    name_variants: list[str]
    name_scientific: str | None
    food_group: str
    state: str
    region_associations: list[str]
    allergens: list[str]
    trust_tier: TrustTier
    source_id: str
    retrieved_at: date
    verification_status: VerificationStatus
    notes: str | None
    energia_kcal: float | None = None
    proteina_g: float | None = None


class FoodDetailOut(FoodOut):
    nutrients: list[NutrientOut]
    source_citation: str | None = None
    allergy_conflicts: list[dict] = []


class PriceIn(BaseModel):
    food_id: str
    product_desc: str
    municipality: str
    market: str | None = None
    commercial_unit: str
    price_cop: float = Field(gt=0)
    observed_at: date
    data_type: Literal["observado", "publicado", "estimado"] = "observado"
    source_desc: str
    confidence: str | None = None


class PriceOut(PriceIn):
    id: int
    created_by: int | None


class RecipeOut(BaseModel):
    id: str
    name: str
    variant_name: str | None
    region: str | None
    servings: int
    time_minutes: int | None
    steps: list[str]
    trust_tier: TrustTier
    source_desc: str
    nutrition_method: str | None
    ingredients: list[dict]
    nutrition_per_serving: dict | None = None


# --- Planificador ---
class MenuRequest(BaseModel):
    days: int = Field(default=1, ge=1, le=7)


class SafetyMessage(BaseModel):
    severity: str
    code: str
    message: str


class PlanOut(BaseModel):
    plan_id: int | None
    status: Literal["ok", "advertencia", "requiere_profesional", "bloqueado", "urgencia"]
    safety_messages: list[SafetyMessage]
    applied_rules: list[str]
    menu: dict | None = None
    nutrition_per_day: dict | None = None
    adequacy: list[dict] | None = None
    pilot_mode: bool
    limitations: list[str]


# --- Seguimiento ---
class TrackingIn(BaseModel):
    entry_date: date
    kind: Literal["consumo", "habito"] = "consumo"
    food_ids: list[str] = []
    note: str | None = None


class TrackingOut(BaseModel):
    id: int
    entry_date: date
    kind: str
    food_ids: list[str]
    note: str | None


class ReviewIn(BaseModel):
    action: Literal["aprobar", "rechazar", "observaciones"]
    notes: str | None = None


class RuleReviewIn(BaseModel):
    action: Literal["aprobar", "rechazar"]
    notes: str | None = None


class EstadoOut(BaseModel):
    version: str
    pilot_mode: bool
    ai_enabled: bool
    rules_total: int
    rules_approved: int
    foods_total: int
    recipes_total: int
    prices_total: int


class ExportOut(BaseModel):
    exported_at: datetime
    user: dict
    profile: dict | None
    allergies: list[dict]
    health_flags: list[dict]
    menu_plans: list[dict]
    tracking: list[dict]
