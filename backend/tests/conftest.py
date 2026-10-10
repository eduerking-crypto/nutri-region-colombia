"""Fixtures: entorno de prueba con BD en memoria y catalogo minimo real."""
from __future__ import annotations

import os

os.environ["NUTRI_DB_URL"] = "sqlite:///:memory:"
os.environ["NUTRI_JWT_SECRET"] = "test-secret-no-produccion"
os.environ["NUTRI_RULES_PILOT_MODE"] = "true"
os.environ["NUTRI_AI_ENABLED"] = "false"
os.environ["NUTRI_ADMIN_EMAIL"] = "admin@example.com"
os.environ["NUTRI_ADMIN_PASSWORD"] = "admin-clave-test-123"

import uuid
from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.db import engine, init_db
from app.models import (
    ClinicalRule,
    Food,
    FoodNutrient,
    Source,
    User,
)
from app.models.catalog import jdumps
from app.security.passwords import hash_password

# Composicion sintetica SOLO para pruebas del motor (nunca se muestra como dato real)
TEST_NUTRIENTS: dict[str, dict[str, float]] = {
    "energia": {"arroz": 365.0, "frijol": 341.0, "yuca": 160.0, "naranja": 47.0, "leche": 61.0, "huevo": 143.0, "pollo": 120.0, "brocoli": 34.0},
    "proteina": {"arroz": 7.1, "frijol": 21.6, "yuca": 1.4, "naranja": 0.9, "leche": 3.2, "huevo": 12.6, "pollo": 22.5, "brocoli": 2.8},
    "grasa_total": {"arroz": 0.7, "frijol": 1.4, "yuca": 0.3, "naranja": 0.1, "leche": 3.3, "huevo": 9.5, "pollo": 1.5, "brocoli": 0.4},
    "carbohidratos": {"arroz": 80.0, "frijol": 62.4, "yuca": 38.1, "naranja": 11.8, "leche": 4.8, "huevo": 0.7, "pollo": 0.0, "brocoli": 6.6},
    "fibra": {"arroz": 1.3, "frijol": 15.5, "yuca": 1.8, "naranja": 2.4, "leche": 0.0, "huevo": 0.0, "pollo": 0.0, "brocoli": 2.6},
}

TEST_FOODS: list[tuple[str, str, str, list[str], str]] = [
    # (id, nombre, grupo, alergenos, slug-nutriente)
    ("FDC-T-ARROZ", "Arroz blanco (prueba)", "cereal", [], "arroz"),
    ("FDC-T-FRIJOL", "Frijol negro (prueba)", "legumbre", [], "frijol"),
    ("FDC-T-YUCA", "Yuca (prueba)", "vegetal", [], "yuca"),
    ("FDC-T-NARANJA", "Naranja (prueba)", "fruta", [], "naranja"),
    ("FDC-T-LECHE", "Leche entera (prueba)", "lacteo", ["leche"], "leche"),
    ("FDC-T-HUEVO", "Huevo (prueba)", "huevo", ["huevo"], "huevo"),
    ("FDC-T-POLLO", "Pollo (prueba)", "proteina_animal", [], "pollo"),
    ("FDC-T-BROCOLI", "Brocoli (prueba)", "vegetal", [], "brocoli"),
]


def seed_test_catalog(session: Session) -> None:
    session.add(
        Source(
            id="SRC-TEST",
            name="Fuente de prueba (solo tests)",
            kind="tabla_composicion",
            version="test",
            license="test",
            access_method="api",
            retrieved_at=date(2026, 1, 1),
        )
    )
    for food_id, name, group, allergens, slug in TEST_FOODS:
        animal = group in {"lacteo", "huevo", "proteina_animal"}
        session.add(
            Food(
                id=food_id,
                name_common=name,
                food_group=group,
                state="crudo",
                allergens=jdumps(allergens),
                diet_tags=jdumps(["animal"] if animal else ["vegetal"]),
                trust_tier="medido",
                source_id="SRC-TEST",
                source_version="test",
                retrieved_at=date(2026, 1, 1),
                notes="Dato sintetico de prueba: no mostrar en produccion.",
            )
        )
        for nutrient, values in TEST_NUTRIENTS.items():
            session.add(
                FoodNutrient(
                    food_id=food_id,
                    nutrient=nutrient,
                    value=values[slug],
                    unit="kcal" if nutrient == "energia" else "g",
                    trust_tier="medido",
                    source_id="SRC-TEST",
                    retrieved_at=date(2026, 1, 1),
                )
            )

    rules = [
        ClinicalRule(
            id="T-DIAB", version=1, scope="test", name="diabetes test",
            conditions='[{"type": "health_flag", "value": "diabetes_medicamentos"}]',
            exceptions="[]", action="derivar_profesional",
            message="Tu situacion requiere acompanamiento profesional de salud (prueba).",
            justification="test", source_desc="test", status="candidate",
        ),
        ClinicalRule(
            id="T-EMB", version=1, scope="test", name="embarazo test",
            conditions='[{"type": "health_flag", "value": "embarazo"}]',
            exceptions="[]", action="derivar_profesional",
            message="El embarazo requiere acompanamiento profesional (prueba).",
            justification="test", source_desc="test", status="approved",
        ),
        ClinicalRule(
            id="T-LACT", version=1, scope="test", name="lactancia test",
            conditions='[{"type": "health_flag", "value": "lactancia"}]',
            exceptions="[]", action="advertir",
            message="En lactancia, el acompanamiento profesional es recomendable (prueba).",
            justification="test", source_desc="test", status="candidate",
        ),
    ]
    for rule in rules:
        session.add(rule)
    session.add(
        User(
            email="admin@example.com",
            password_hash=hash_password("admin-clave-test-123"),
            role="admin",
            display_name="Admin de prueba",
        )
    )
    session.commit()


@pytest.fixture(scope="session", autouse=True)
def base_de_datos():
    """Inicializa y siembra la BD en memoria UNA VEZ para toda la sesion."""
    init_db()
    with Session(engine) as session:
        seed_test_catalog(session)
    yield


@pytest.fixture(scope="session")
def client():
    from app.main import app

    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def usuario_prueba(client):
    """Crea un usuario y devuelve (email, password, headers)."""
    email = f"usuario-{uuid.uuid4().hex[:10]}@example.com"
    password = "clave-segura-123"
    response = client.post(
        "/api/auth/registro",
        json={"email": email, "password": password, "accept_consent": True},
    )
    assert response.status_code == 201, response.text
    token = response.json()["access_token"]
    return email, password, {"Authorization": f"Bearer {token}"}


def login(client, email: str, password: str) -> dict:
    response = client.post("/api/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}
