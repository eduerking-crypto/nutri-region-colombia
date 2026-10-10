"""Configuracion de privacidad: exportacion y eliminacion de la cuenta."""
from __future__ import annotations

import json
from datetime import UTC, datetime

from fastapi import APIRouter, status
from sqlmodel import select

from app.api.deps import CurrentUser, SessionDep
from app.models import (
    AuditLog,
    MenuPlan,
    TrackingEntry,
    UserAllergy,
    UserHealthFlag,
    UserProfile,
)
from app.schemas import ExportOut

router = APIRouter(prefix="/configuracion", tags=["configuracion"])


@router.get("/datos", response_model=ExportOut)
def exportar_datos(session: SessionDep, user: CurrentUser) -> ExportOut:
    """Exporta TODOS los datos personales del usuario (derecho de acceso)."""
    profile = session.exec(
        select(UserProfile).where(UserProfile.user_id == user.id)
    ).first()
    allergies = session.exec(select(UserAllergy).where(UserAllergy.user_id == user.id)).all()
    flags = session.exec(select(UserHealthFlag).where(UserHealthFlag.user_id == user.id)).all()
    plans = session.exec(select(MenuPlan).where(MenuPlan.user_id == user.id)).all()
    tracking = session.exec(select(TrackingEntry).where(TrackingEntry.user_id == user.id)).all()
    return ExportOut(
        exported_at=datetime.now(UTC),
        user={
            "email": user.email,
            "display_name": user.display_name,
            "role": user.role,
            "consent_version": user.consent_version,
            "consent_at": user.consent_at.isoformat() if user.consent_at else None,
            "created_at": user.created_at.isoformat(),
        },
        profile=json.loads(profile.model_dump_json()) if profile else None,
        allergies=[
            {
                "allergen": item.allergen,
                "kind": item.kind,
                "severity": item.severity,
                "notes": item.notes,
            }
            for item in allergies
        ],
        health_flags=[
            {"flag": item.flag, "self_reported": item.self_reported, "notes": item.notes}
            for item in flags
        ],
        menu_plans=[
            {
                "created_at": item.created_at.isoformat(),
                "status": item.status,
                "days": item.days_list,
            }
            for item in plans
        ],
        tracking=[
            {
                "entry_date": str(item.entry_date),
                "kind": item.kind,
                "content": item.content_dict,
            }
            for item in tracking
        ],
    )


@router.delete("/cuenta", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_cuenta(session: SessionDep, user: CurrentUser) -> None:
    """Elimina la cuenta y TODOS sus datos asociados (derecho de supresion).

    Deja un registro de auditoria sin datos personales: solo el hecho.
    """
    user_id = user.id
    for item in session.exec(select(TrackingEntry).where(TrackingEntry.user_id == user_id)).all():
        session.delete(item)
    for item in session.exec(select(MenuPlan).where(MenuPlan.user_id == user_id)).all():
        session.delete(item)
    for item in session.exec(select(UserHealthFlag).where(UserHealthFlag.user_id == user_id)).all():
        session.delete(item)
    for item in session.exec(select(UserAllergy).where(UserAllergy.user_id == user_id)).all():
        session.delete(item)
    profile = session.exec(
        select(UserProfile).where(UserProfile.user_id == user_id)
    ).first()
    if profile:
        session.delete(profile)
    session.delete(user)
    session.add(
        AuditLog(
            actor=f"user:{user_id}",
            entity="user",
            entity_id=str(user_id),
            action="cuenta_eliminada",
            details="Datos personales eliminados en ejercicio del derecho de supresion.",
        )
    )
    session.commit()
