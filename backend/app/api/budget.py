"""Presupuesto y lista de compras con precios honestos (ADR-0007)."""
from __future__ import annotations

from datetime import date

from fastapi import APIRouter, HTTPException
from sqlmodel import select

from app.api.deps import CurrentUser, SessionDep
from app.models import MenuPlan, PriceObservation
from app.schemas import PriceIn, PriceOut

router = APIRouter(prefix="/presupuesto", tags=["presupuesto"])


@router.post("/precios", response_model=PriceOut, status_code=201)
def registrar_precio(payload: PriceIn, session: SessionDep, user: CurrentUser) -> PriceOut:
    """Registra una observacion de precio con fecha, fuente y tipo de dato."""
    if payload.observed_at > date.today():
        raise HTTPException(status_code=422, detail="La fecha de observacion no puede ser futura.")
    item = PriceObservation(
        food_id=payload.food_id,
        product_desc=payload.product_desc,
        municipality=payload.municipality,
        market=payload.market,
        commercial_unit=payload.commercial_unit,
        price_cop=payload.price_cop,
        observed_at=payload.observed_at,
        data_type=payload.data_type,
        source_desc=payload.source_desc,
        confidence=payload.confidence,
        created_by=user.id,
    )
    session.add(item)
    session.commit()
    session.refresh(item)
    return PriceOut(**payload.model_dump(), id=item.id, created_by=user.id)


@router.get("/precios", response_model=list[PriceOut])
def listar_precios(
    session: SessionDep,
    municipality: str | None = None,
    food_id: str | None = None,
) -> list[PriceOut]:
    """Listado publico de observaciones de precio. Sin datos -> lista vacia."""
    query = select(PriceObservation)
    if municipality:
        query = query.where(PriceObservation.municipality == municipality)
    if food_id:
        query = query.where(PriceObservation.food_id == food_id)
    items = session.exec(query.order_by(PriceObservation.observed_at.desc())).all()  # type: ignore[union-attr]
    return [
        PriceOut(
            food_id=item.food_id,
            product_desc=item.product_desc,
            municipality=item.municipality,
            market=item.market,
            commercial_unit=item.commercial_unit,
            price_cop=item.price_cop,
            observed_at=item.observed_at,
            data_type=item.data_type,
            source_desc=item.source_desc,
            confidence=item.confidence,
            id=item.id,
            created_by=item.created_by,
        )
        for item in items
    ]


@router.post("/{plan_id}/costo")
def costo_plan(plan_id: int, session: SessionDep, user: CurrentUser) -> dict:
    """Costo estimado del plan con los precios disponibles. Honesto por diseno."""
    plan = session.get(MenuPlan, plan_id)
    if plan is None or plan.user_id != user.id:
        raise HTTPException(status_code=404, detail="Plan no encontrado.")
    import json

    menu = json.loads(plan.days or "{}")
    shopping = menu.get("lista_compras") or {}
    if not shopping:
        return {
            "plan_id": plan_id,
            "total_cop": None,
            "items_con_precio": 0,
            "items_sin_precio": 0,
            "aviso": "Este plan no tiene lista de compras (posiblemente bloqueado por seguridad).",
        }

    profile_municipality = None
    from app.models import UserProfile

    profile = session.exec(select(UserProfile).where(UserProfile.user_id == user.id)).first()
    if profile:
        profile_municipality = profile.municipality

    total = 0.0
    con_precio = 0
    sin_precio = 0
    items = []
    for food_id, item in sorted(shopping.items()):
        query = select(PriceObservation).where(PriceObservation.food_id == food_id)
        if profile_municipality:
            query = query.where(PriceObservation.municipality == profile_municipality)
        price = session.exec(
            query.order_by(PriceObservation.observed_at.desc())  # type: ignore[union-attr]
        ).first()
        if price is None:
            # fallback: ultima observacion en cualquier municipio, marcandola
            price = session.exec(
                select(PriceObservation)
                .where(PriceObservation.food_id == food_id)
                .order_by(PriceObservation.observed_at.desc())  # type: ignore[union-attr]
            ).first()
            if price is not None:
                items.append(
                    {
                        "food_id": food_id,
                        "name": item.get("name"),
                        "grams": item.get("grams"),
                        "price_cop": price.price_cop,
                        "price_date": str(price.observed_at),
                        "data_type": price.data_type,
                        "aviso": (
                            "Precio de otro municipio ("
                            f"{price.municipality}); tipo: {price.data_type}."
                        ),
                    }
                )
                total += price.price_cop
                con_precio += 1
                continue
        if price is None:
            items.append(
                {
                    "food_id": food_id,
                    "name": item.get("name"),
                    "grams": item.get("grams"),
                    "price_cop": None,
                    "aviso": "Sin datos de precio para este alimento.",
                }
            )
            sin_precio += 1
        else:
            items.append(
                {
                    "food_id": food_id,
                    "name": item.get("name"),
                    "grams": item.get("grams"),
                    "price_cop": price.price_cop,
                    "price_date": str(price.observed_at),
                    "data_type": price.data_type,
                }
            )
            total += price.price_cop
            con_precio += 1

    return {
        "plan_id": plan_id,
        "total_cop": total if con_precio else None,
        "items_con_precio": con_precio,
        "items_sin_precio": sin_precio,
        "aviso": (
            "Costo parcial: solo se suman alimentos con precio observado/publicado. "
            "Los precios muestran fecha y tipo de dato; nunca se interpolan por ubicacion."
            if sin_precio
            else "Costo calculado con precios observados/publicados disponibles."
        ),
        "items": items,
    }
