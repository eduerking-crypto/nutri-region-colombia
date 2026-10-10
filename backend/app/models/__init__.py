"""Registro de modelos."""
from app.models.catalog import (
    Evidence,
    Food,
    FoodNutrient,
    PriceObservation,
    Recipe,
    RecipeIngredient,
    Source,
)
from app.models.rules import ClinicalRule
from app.models.user import (
    AuditLog,
    MenuPlan,
    TrackingEntry,
    User,
    UserAllergy,
    UserHealthFlag,
    UserProfile,
)

__all__ = [
    "AuditLog",
    "ClinicalRule",
    "Evidence",
    "Food",
    "FoodNutrient",
    "MenuPlan",
    "PriceObservation",
    "Recipe",
    "RecipeIngredient",
    "Source",
    "TrackingEntry",
    "User",
    "UserAllergy",
    "UserHealthFlag",
    "UserProfile",
]
