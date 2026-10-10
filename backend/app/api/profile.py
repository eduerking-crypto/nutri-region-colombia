"""Perfil adaptativo: contexto territorial, preferencias, alergias, salud."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, status
from sqlmodel import select

from app.api.deps import CurrentUser, SessionDep
from app.models import (
    TrackingEntry,
    UserAllergy,
    UserHealthFlag,
    UserProfile,
)
from app.models.catalog import jdumps
from app.schemas import (
    AllergyIn,
    AllergyOut,
    HealthFlagIn,
    HealthFlagOut,
    ProfileIn,
    ProfileOut,
    TrackingIn,
    TrackingOut,
)

router = APIRouter(prefix="/perfil", tags=["perfil"])


def _get_or_create_profile(session, user_id: int) -> UserProfile:
    profile = session.exec(
        select(UserProfile).where(UserProfile.user_id == user_id)
    ).first()
    if profile is None:
        profile = UserProfile(user_id=user_id)
        session.add(profile)
        session.flush()
    return profile


@router.get("", response_model=ProfileOut)
def obtener_perfil(session: SessionDep, user: CurrentUser) -> ProfileOut:
    profile = _get_or_create_profile(session, user.id)
    return ProfileOut(
        user_id=profile.user_id,
        department=profile.department,
        municipality=profile.municipality,
        zone=profile.zone,
        household_size=profile.household_size,
        budget_weekly_cop=profile.budget_weekly_cop,
        cooking_time_minutes=profile.cooking_time_minutes,
        has_refrigeration=profile.has_refrigeration,
        meals_per_day=profile.meals_per_day,
        dietary_pattern=profile.dietary_pattern,
        preferred_foods=profile.preferred_list,
        rejected_foods=profile.rejected_list,
        onboarding_completed=profile.onboarding_completed,
    )


@router.put("", response_model=ProfileOut)
def actualizar_perfil(payload: ProfileIn, session: SessionDep, user: CurrentUser) -> ProfileOut:
    profile = _get_or_create_profile(session, user.id)
    data = payload.model_dump()
    data["preferred_foods"] = jdumps(data["preferred_foods"])
    data["rejected_foods"] = jdumps(data["rejected_foods"])
    for key, value in data.items():
        setattr(profile, key, value)
    session.add(profile)
    session.commit()
    session.refresh(profile)
    return obtener_perfil(session=session, user=user)


@router.get("/alergias", response_model=list[AllergyOut])
def listar_alergias(session: SessionDep, user: CurrentUser) -> list[AllergyOut]:
    items = session.exec(select(UserAllergy).where(UserAllergy.user_id == user.id)).all()
    return [
        AllergyOut(
            id=item.id, allergen=item.allergen, kind=item.kind,
            severity=item.severity, notes=item.notes,
        )
        for item in items
    ]


@router.post("/alergias", response_model=AllergyOut, status_code=status.HTTP_201_CREATED)
def agregar_alergia(payload: AllergyIn, session: SessionDep, user: CurrentUser) -> AllergyOut:
    existing = session.exec(
        select(UserAllergy).where(
            UserAllergy.user_id == user.id, UserAllergy.allergen == payload.allergen
        )
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Ese alergeno ya esta registrado.")
    item = UserAllergy(user_id=user.id, **payload.model_dump())
    session.add(item)
    session.commit()
    session.refresh(item)
    return AllergyOut(**payload.model_dump(), id=item.id)


@router.delete("/alergias/{alergia_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_alergia(alergia_id: int, session: SessionDep, user: CurrentUser) -> None:
    item = session.get(UserAllergy, alergia_id)
    if item is None or item.user_id != user.id:
        raise HTTPException(status_code=404, detail="Alergia no encontrada.")
    session.delete(item)
    session.commit()


@router.get("/salud", response_model=list[HealthFlagOut])
def listar_salud(session: SessionDep, user: CurrentUser) -> list[HealthFlagOut]:
    items = session.exec(select(UserHealthFlag).where(UserHealthFlag.user_id == user.id)).all()
    return [HealthFlagOut(id=item.id, flag=item.flag, self_reported=item.self_reported, notes=item.notes) for item in items]


@router.post("/salud", response_model=HealthFlagOut, status_code=status.HTTP_201_CREATED)
def agregar_salud(payload: HealthFlagIn, session: SessionDep, user: CurrentUser) -> HealthFlagOut:
    existing = session.exec(
        select(UserHealthFlag).where(
            UserHealthFlag.user_id == user.id, UserHealthFlag.flag == payload.flag
        )
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Ese indicador ya esta registrado.")
    item = UserHealthFlag(user_id=user.id, **payload.model_dump())
    session.add(item)
    session.commit()
    session.refresh(item)
    return HealthFlagOut(**payload.model_dump(), id=item.id)


@router.delete("/salud/{flag_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_salud(flag_id: int, session: SessionDep, user: CurrentUser) -> None:
    item = session.get(UserHealthFlag, flag_id)
    if item is None or item.user_id != user.id:
        raise HTTPException(status_code=404, detail="Indicador no encontrado.")
    session.delete(item)
    session.commit()


# --- Seguimiento de habitos ---
@router.post("/seguimiento", response_model=TrackingOut, status_code=status.HTTP_201_CREATED)
def registrar_seguimiento(payload: TrackingIn, session: SessionDep, user: CurrentUser) -> TrackingOut:
    item = TrackingEntry(
        user_id=user.id,
        entry_date=payload.entry_date,
        kind=payload.kind,
        content=jdumps([{"food_ids": payload.food_ids, "note": payload.note}]),
    )
    session.add(item)
    session.commit()
    session.refresh(item)
    return TrackingOut(
        id=item.id, entry_date=item.entry_date, kind=item.kind,
        food_ids=payload.food_ids, note=payload.note,
    )


@router.get("/seguimiento", response_model=list[TrackingOut])
def listar_seguimiento(
    session: SessionDep, user: CurrentUser, limit: int = 60
) -> list[TrackingOut]:
    items = session.exec(
        select(TrackingEntry)
        .where(TrackingEntry.user_id == user.id)
        .order_by(TrackingEntry.entry_date.desc())  # type: ignore[union-attr]
    ).all()
    result = []
    for item in items[:limit]:
        content = item.content_dict
        payload = content[0] if isinstance(content, list) and content else {}
        result.append(
            TrackingOut(
                id=item.id, entry_date=item.entry_date, kind=item.kind,
                food_ids=payload.get("food_ids", []), note=payload.get("note"),
            )
        )
    return result
