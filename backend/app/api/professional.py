"""Panel profesional: revision de planes y aprobacion de reglas candidatas.

La aprobacion de reglas queda registrada con revisor y fecha. NOTA HONESTA:
esta plataforma no verifica credenciales profesionales; esa verificacion es
un pendiente explicito (PD-11) antes de produccion.
"""
from __future__ import annotations

from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import select

from app.api.deps import SessionDep, require_role
from app.models import AuditLog, ClinicalRule, MenuPlan, User

router = APIRouter(prefix="/profesional", tags=["profesional"])

ProfesionalUser = Annotated[User, Depends(require_role("profesional", "admin"))]


class RevisionIn(BaseModel):
    action: str  # aprobar | rechazar | observaciones
    notes: str | None = None


@router.get("/planes")
def planes_pendientes(session: SessionDep, user: ProfesionalUser) -> list[dict]:
    plans = session.exec(
        select(MenuPlan)
        .where(MenuPlan.status == "pendiente_revision")  # type: ignore[attr-defined]
        .order_by(MenuPlan.created_at.asc())  # type: ignore[union-attr]
    ).all()
    return [
        {
            "plan_id": plan.id,
            "user_id": plan.user_id,
            "created_at": plan.created_at.isoformat(),
            "status": plan.status,
            "warnings": plan.warnings_list,
            "triage_result": plan.triage_result,
        }
        for plan in plans
    ]


@router.post("/planes/{plan_id}/revision")
def revisar_plan(
    plan_id: int, payload: RevisionIn, session: SessionDep, user: ProfesionalUser
) -> dict:
    plan = session.get(MenuPlan, plan_id)
    if plan is None:
        raise HTTPException(status_code=404, detail="Plan no encontrado.")
    if payload.action not in {"aprobar", "rechazar", "observaciones"}:
        raise HTTPException(
            status_code=422, detail="Accion invalida: aprobar | rechazar | observaciones."
        )
    plan.status = {
        "aprobar": "aprobado",
        "rechazar": "rechazado",
        "observaciones": "pendiente_revision",
    }[payload.action]
    plan.reviewer_id = user.id
    plan.review_notes = payload.notes
    plan.reviewed_at = datetime.now(UTC)
    session.add(plan)
    session.add(
        AuditLog(
            actor=f"user:{user.id}",
            entity="menu_plan",
            entity_id=str(plan.id),
            action=f"revision:{payload.action}",
            details=payload.notes,
        )
    )
    session.commit()
    return {"plan_id": plan.id, "status": plan.status, "reviewer_id": user.id}


@router.post("/reglas/{rule_id}/aprobar")
def aprobar_regla(
    rule_id: str, session: SessionDep, user: ProfesionalUser, notes: str | None = None
) -> dict:
    """Aprueba una regla candidata. Queda registrado quien y cuando."""
    rule = session.get(ClinicalRule, rule_id)
    if rule is None:
        raise HTTPException(status_code=404, detail="Regla no encontrada.")
    if rule.status == "approved":
        raise HTTPException(status_code=409, detail="La regla ya esta aprobada.")
    rule.status = "approved"
    rule.reviewer = user.email
    rule.approved_at = datetime.now(UTC)
    session.add(rule)
    session.add(
        AuditLog(
            actor=f"user:{user.id}",
            entity="clinical_rule",
            entity_id=rule.id,
            action="approved",
            details=notes,
        )
    )
    session.commit()
    return {"rule_id": rule.id, "status": rule.status, "reviewer": rule.reviewer}
