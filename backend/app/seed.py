"""Sembrado idempotente de datos reales y configuracion.

Fuentes:
- data/imports/fdc/normalized.json  (alimentos reales USDA FDC + informe de calidad)
- data/rules/rules.json              (reglas candidatas del motor)
- data/recipes/recipes.json          (recetario educativo con IDs por slug)

NO inventa datos: si un archivo no existe, se salta con aviso.
"""
from __future__ import annotations

import json
from datetime import date

from sqlmodel import Session, select

from app import config
from app.db import engine, init_db
from app.models import (
    AuditLog,
    ClinicalRule,
    Evidence,
    Food,
    FoodNutrient,
    Recipe,
    RecipeIngredient,
    Source,
    User,
    UserProfile,
)
from app.models.catalog import jdumps
from app.security.passwords import hash_password

RECIPES_PATH = config.DATA_DIR / "recipes" / "recipes.json"
RULES_PATH = config.DATA_DIR / "rules" / "rules.json"


def seed_sources(session: Session, normalized: dict) -> dict:
    created: dict[str, Source] = {}
    meta = normalized.get("meta", {}).get("source", {})
    fdc = Source(
        id=meta.get("id", "SRC-USDA-FDC"),
        name=meta.get("name", "USDA FoodData Central"),
        kind="tabla_composicion",
        version="SR Legacy 2019 + Foundation (por alimento)",
        license="Dominio publico (datos del gobierno de EE. UU.)",
        redistribution_allowed=True,
        access_method="api",
        url=meta.get("url"),
        citation=meta.get("citation"),
        retrieved_at=date.fromisoformat(normalized["meta"]["retrieved_at"]),
        notes="Fuente verificada y usada en el catalogo actual.",
    )
    if session.get(Source, fdc.id) is None:
        session.add(fdc)
    created[fdc.id] = fdc

    pendientes = [
        (
            "SRC-ICBF-PEND",
            "Tabla de Composicion de Alimentos Colombianos (ICBF)",
            "tabla_composicion",
            "Fuente prioritaria para el producto. Version vigente, metodo de acceso y licencia/permiso de redistribucion PENDIENTES DE VERIFICACION (PD-04). Sin datos cargados todavia.",
        ),
        (
            "SRC-FAO-INFOODS-PEND",
            "FAO/INFOODS — Tablas de composicion de alimentos",
            "tabla_composicion",
            "Cobertura internacional. Licencia y acceso por verificar (PD-04). Sin datos cargados todavia.",
        ),
    ]
    for source_id, name, kind, notes in pendientes:
        if session.get(Source, source_id) is None:
            session.add(
                Source(
                    id=source_id,
                    name=name,
                    kind=kind,
                    version="por verificar",
                    license="por verificar",
                    redistribution_allowed=False,
                    access_method="consulta_manual",
                    retrieved_at=date.today(),
                    notes=notes,
                )
            )
    session.flush()
    return created


def seed_foods(session: Session, normalized: dict, source: Source) -> int:
    count = 0
    for food_data in normalized.get("foods", []):
        if session.get(Food, food_data["id"]) is not None:
            continue
        food = Food(
            id=food_data["id"],
            name_common=food_data["name_common"],
            name_variants=jdumps(food_data.get("name_variants", [])),
            name_scientific=food_data.get("name_scientific"),
            food_group=food_data["food_group"],
            state=food_data["state"],
            region_associations=jdumps(food_data.get("region_associations", [])),
            external_ids=jdumps(
                [
                    {"source": "FDC", "id": food_data["id"].replace("FDC-", "")},
                    {"source": "FDC-description", "id": food_data.get("fdc_description")},
                ]
            ),
            allergens=jdumps(food_data.get("allergens", [])),
            diet_tags=jdumps(food_data.get("diet_tags", [])),
            trust_tier="medido",
            source_id=source.id,
            source_version=str(food_data.get("fdc_data_type", "")),
            retrieved_at=date.fromisoformat(normalized["meta"]["retrieved_at"]),
            verification_status="unverified",
            notes=(
                f"Descripcion FDC: {food_data.get('fdc_description')}. "
                f"{food_data.get('notes', '')}"
            ),
        )
        session.add(food)
        for nutrient in food_data.get("nutrients", []):
            session.add(
                FoodNutrient(
                    food_id=food.id,
                    nutrient=nutrient["nutrient"],
                    value=nutrient["value"],
                    unit=nutrient["unit"],
                    method=nutrient.get("method"),
                    trust_tier=nutrient["trust_tier"],
                    source_id=source.id,
                    retrieved_at=date.fromisoformat(normalized["meta"]["retrieved_at"]),
                    verification_status="unverified",
                )
            )
        count += 1
    return count


def seed_evidence(session: Session) -> int:
    items = [
        Evidence(
            id="EV-OMS-TRS916",
            title="Dieta, nutricion y prevencion de enfermedades cronicas (rangos de macronutrientes)",
            citation=(
                "OMS/FAO. Diet, nutrition and the prevention of chronic diseases. "
                "Informe Tecnico 916. Ginebra, 2003."
            ),
            study_type="informe tecnico de organismo internacional",
            relevant_finding=(
                "Rangos de referencia de distribucion de energia: carbohidratos 55-75 %, "
                "proteinas 10-15 %, grasas 15-30 %. Usados por el motor como referencia "
                "NO vinculante para evaluar menus."
            ),
            limitations=(
                "Cita registrada de referencia general por el equipo; verificar edicion, "
                "paginas y vigencia con el documento oficial antes de produccion (PD-11). "
                "No reemplaza recomendaciones individualizadas."
            ),
            trust_tier="literatura",
            reviewed_at=date.today(),
            verification_status="unverified",
            notes="Referencia usada por app.engine.calc.REFERENCE_RANGES.",
        ),
        Evidence(
            id="EV-USDA-FDC",
            title="USDA FoodData Central (fuente del catalogo actual)",
            citation=(
                "U.S. Department of Agriculture, Agricultural Research Service. "
                "FoodData Central. https://fdc.nal.usda.gov/"
            ),
            stable_url="https://fdc.nal.usda.gov/",
            relevant_finding="Fuente de composicion de los alimentos del catalogo (SR Legacy y Foundation).",
            limitations=(
                "Muestras de EE. UU.; composicion mayormente de alimentos crudos; "
                "las condiciones colombianas pueden diferir."
            ),
            trust_tier="literatura",
            reviewed_at=date.today(),
            verification_status="verified",
        ),
    ]
    count = 0
    for item in items:
        if session.get(Evidence, item.id) is None:
            session.add(item)
            count += 1
    return count


def seed_rules(session: Session) -> int:
    if not RULES_PATH.exists():
        print(f"AVISO: {RULES_PATH} no existe; no se sembraron reglas.")
        return 0
    data = json.loads(RULES_PATH.read_text(encoding="utf-8-sig"))
    count = 0
    for rule_data in data.get("reglas", []):
        rule_id = rule_data["id"]
        existing = session.get(ClinicalRule, rule_id)
        if existing is not None:
            continue
        session.add(
            ClinicalRule(
                id=rule_id,
                version=rule_data.get("version", 1),
                scope=rule_data.get("scope", "salud"),
                name=rule_data["name"],
                conditions=json.dumps(rule_data.get("conditions", []), ensure_ascii=False),
                exceptions=json.dumps(rule_data.get("exceptions", []), ensure_ascii=False),
                action=rule_data["action"],
                message=rule_data["message"],
                justification=rule_data.get("justification", ""),
                source_desc=rule_data.get("source_desc", ""),
                evidence_level=rule_data.get("evidence_level", "pendiente_verificacion"),
                status=rule_data.get("status", "candidate"),
            )
        )
        count += 1
    return count


def seed_recipes(session: Session, normalized: dict) -> int:
    if not RECIPES_PATH.exists():
        print(f"AVISO: {RECIPES_PATH} no existe; no se sembraron recetas.")
        return 0
    slug_to_id = {
        food_data["slug"]: food_data["id"]
        for food_data in normalized.get("foods", [])
        if food_data.get("slug")
    }
    data = json.loads(RECIPES_PATH.read_text(encoding="utf-8-sig"))
    count = 0
    for recipe_data in data.get("recetas", []):
        recipe_id = recipe_data["id"]
        if session.get(Recipe, recipe_id) is not None:
            continue
        resolved = []
        missing = []
        for ingredient in recipe_data.get("ingredients", []):
            slug = ingredient["food_id"].replace("FDC-", "")
            food_id = slug_to_id.get(slug)
            if food_id is None:
                missing.append(slug)
            else:
                resolved.append((ingredient, food_id))
        if missing:
            print(
                f"AVISO: receta {recipe_id} omitida; ingredientes sin datos todavia: {missing}"
            )
            continue
        recipe = Recipe(
            id=recipe_id,
            name=recipe_data["name"],
            region=recipe_data.get("region"),
            servings=recipe_data["servings"],
            time_minutes=recipe_data.get("time_minutes"),
            steps=jdumps(recipe_data.get("steps", [])),
            origin_notes=recipe_data.get("origin_notes"),
            nutrition_method=(
                "Suma de composicion de ingredientes crudos (USDA FDC) por porcion; "
                "no incluye cambios por coccion."
            ),
            trust_tier="educativo",
            source_desc=(
                "Recetario educativo del proyecto (verificacion cultural pendiente, PD-13)."
            ),
            retrieved_at=date.today(),
            verification_status="unverified",
        )
        session.add(recipe)
        for ingredient, food_id in resolved:
            session.add(
                RecipeIngredient(
                    recipe_id=recipe_id,
                    food_id=food_id,
                    quantity_g=ingredient["quantity_g"],
                    unit_note=ingredient.get("unit_note"),
                )
            )
        count += 1
    return count


def seed_admin(session: Session) -> None:
    admin = session.exec(select(User).where(User.email == config.ADMIN_EMAIL)).first()
    if admin is None:
        user = User(
            email=config.ADMIN_EMAIL,
            password_hash=hash_password(config.ADMIN_PASSWORD),
            role="admin",
            display_name="Administracion (desarrollo)",
        )
        session.add(user)
        session.flush()
        session.add(UserProfile(user_id=user.id))
        print(f"Cuenta admin creada: {config.ADMIN_EMAIL} (cambia la clave en produccion)")


def run() -> None:
    init_db()
    with Session(engine) as session:
        normalized = {}
        if config.FDC_NORMALIZED.exists():
            normalized = json.loads(
                config.FDC_NORMALIZED.read_text(encoding="utf-8-sig")
            )
        else:
            print("AVISO: normalized.json no existe; sin alimentos para sembrar.")
        sources = seed_sources(session, normalized)
        foods_count = 0
        if normalized:
            fdc_source = sources.get(normalized.get("meta", {}).get("source", {}).get("id", "SRC-USDA-FDC"))
            if fdc_source:
                foods_count = seed_foods(session, normalized, fdc_source)
        evidence_count = seed_evidence(session)
        rules_count = seed_rules(session)
        recipes_count = seed_recipes(session, normalized)
        seed_admin(session)
        session.add(
            AuditLog(
                actor="seed",
                entity="sistema",
                entity_id="seed",
                action="seed_ejecutado",
                details=(
                    f"alimentos={foods_count} evidencia={evidence_count} "
                    f"reglas={rules_count} recetas={recipes_count}"
                ),
            )
        )
        session.commit()
        print(
            f"Seed completado: alimentos={foods_count}, evidencia={evidence_count}, "
            f"reglas={rules_count}, recetas={recipes_count}"
        )


if __name__ == "__main__":
    run()
