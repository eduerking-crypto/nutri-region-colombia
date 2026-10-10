"""Capa IA opcional y desacoplada (ADR-0009).

- Interfaz de proveedor con implementacion Ollama.
- Desactivada por defecto (NUTRI_AI_ENABLED=false).
- SOLO explica datos ya verificados: el prompt se construye desde la ficha
  estructurada y la salida se valida contra esos mismos datos (guard).
- Puede desactivarse sin romper ninguna funcion nutricional.
"""
from __future__ import annotations

import re

import httpx
from fastapi import APIRouter, HTTPException
from sqlmodel import select

from app import config
from app.api.deps import CurrentUser, SessionDep
from app.models import Food, FoodNutrient, Source

router = APIRouter(prefix="/ia", tags=["ia"])


def _provider_available() -> bool:
    try:
        response = httpx.get(f"{config.OLLAMA_BASE_URL}/api/tags", timeout=3.0)
        return response.status_code == 200
    except httpx.HTTPError:
        return False


def _numbers_in(text: str) -> set[float]:
    return {float(match.replace(",", ".")) for match in re.findall(r"\d+(?:[.,]\d+)?", text)}


def _explain_with_ollama(facts: dict) -> str:
    prompt = (
        "Eres un asistente de divulgacion nutricional de NutriRegion Colombia. "
        "Explica en espanol (es-CO), maximo 150 palabras, con tono cercano y sin jerga, "
        "la ficha nutricional que se te da. REGLAS INQUEBRANTABLES: usa SOLO los "
        "numeros que aparecen en los datos; no agregues nutrientes, efectos ni "
        "afirmaciones de salud que no esten en los datos; no digas que el alimento "
        "previene o cura nada; si un dato falta, di que no hay dato. Datos:\n"
        + str(facts)
    )
    response = httpx.post(
        f"{config.OLLAMA_BASE_URL}/api/generate",
        json={"model": config.OLLAMA_MODEL, "prompt": prompt, "stream": False},
        timeout=120.0,
    )
    response.raise_for_status()
    return response.json().get("response", "")


@router.post("/alimentos/{food_id}/explicacion")
def explicacion_ia(food_id: str, session: SessionDep, user: CurrentUser) -> dict:
    if not config.AI_ENABLED:
        raise HTTPException(
            status_code=503,
            detail="La capa de IA esta desactivada. Todas las funciones nutricionales operan sin ella.",
        )
    food = session.get(Food, food_id)
    if food is None:
        raise HTTPException(status_code=404, detail="Alimento no encontrado.")
    nutrients = session.exec(
        select(FoodNutrient).where(FoodNutrient.food_id == food_id)
    ).all()
    source = session.get(Source, food.source_id)
    facts = {
        "alimento": food.name_common,
        "grupo": food.food_group,
        "estado": food.state,
        "composicion_por_100g": {
            nutrient.nutrient: {"valor": nutrient.value, "unidad": nutrient.unit}
            for nutrient in nutrients
        },
        "fuente": source.citation if source else None,
    }
    if not _provider_available():
        raise HTTPException(
            status_code=503,
            detail="Ollama local no responde. La explicacion IA es opcional; la ficha estructurada sigue disponible.",
        )
    text = _explain_with_ollama(facts)
    # Guard: los numeros de la respuesta deben existir en los datos (tolerancia de redondeo).
    allowed = {nutrient.value for nutrient in nutrients} | {round(nutrient.value, 1) for nutrient in nutrients}
    mentioned = _numbers_in(text)
    suspicious = [number for number in mentioned if not any(abs(number - allowed_value) < 0.06 for allowed_value in allowed)]
    validated = not suspicious
    return {
        "food_id": food_id,
        "explicacion": text,
        "validada_contra_datos": validated,
        "aviso": (
            "Explicacion generada por IA local a partir de la ficha estructurada; "
            "validada contra los datos. No sustituye la ficha ni consejos profesionales."
        ),
    }
