"""Panel administrativo: auditoria, estadisticas y gestion de reglas."""
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select

from app.api.deps import SessionDep, require_role
from app.models import (
    AuditLog,
    ClinicalRule,
    Food,
    PriceObservation,
    Recipe,
    Source,
    User,
    UserAllergy,
    UserHealthFlag,
)

router = APIRouter(prefix="/admin", tags=["admin"])

AdminUser = Annotated[User, Depends(require_role("admin"))]


@router.get("/estadisticas")
def estadisticas(session: SessionDep, user: AdminUser) -> dict:
    users = session.exec(select(User)).all()
    return {
        "usuarios_total": len(users),
        "usuarios_con_alergias": len(
            {item.user_id for item in session.exec(select(UserAllergy)).all()}
        ),
        "usuarios_con_indicadores_salud": len(
            {item.user_id for item in session.exec(select(UserHealthFlag)).all()}
        ),
        "alimentos_total": len(session.exec(select(Food)).all()),
        "recetas_total": len(session.exec(select(Recipe)).all()),
        "fuentes_total": len(session.exec(select(Source)).all()),
        "precios_total": len(session.exec(select(PriceObservation)).all()),
        "reglas_total": len(session.exec(select(ClinicalRule)).all()),
        "reglas_aprobadas": len(
            [rule for rule in session.exec(select(ClinicalRule)).all() if rule.status == "approved"]
        ),
    }


@router.get("/auditoria")
def auditoria(session: SessionDep, user: AdminUser, limit: int = 100) -> list[dict]:
    logs = session.exec(
        select(AuditLog).order_by(AuditLog.at.desc())  # type: ignore[union-attr]
    ).all()
    return [
        {
            "id": log.id,
            "at": log.at.isoformat(),
            "actor": log.actor,
            "entity": log.entity,
            "entity_id": log.entity_id,
            "action": log.action,
            "details": log.details,
        }
        for log in logs[:limit]
    ]


@router.post("/usuarios/{user_id}/rol")
def cambiar_rol(
    user_id: int, role: str, session: SessionDep, user: AdminUser
) -> dict:
    if role not in {"usuario", "profesional", "admin"}:
        raise HTTPException(status_code=422, detail="Rol invalido.")
    target = session.get(User, user_id)
    if target is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    previous = target.role
    target.role = role
    session.add(target)
    session.add(
        AuditLog(
            actor=f"user:{user.id}",
            entity="user",
            entity_id=str(target.id),
            action=f"role:{previous}->{role}",
        )
    )
    session.commit()
    return {"user_id": target.id, "role": target.role}


@router.post("/reglas/{rule_id}/retirar")
def retirar_regla(rule_id: str, session: SessionDep, user: AdminUser) -> dict:
    rule = session.get(ClinicalRule, rule_id)
    if rule is None:
        raise HTTPException(status_code=404, detail="Regla no encontrada.")
    if rule.status == "approved":
        raise HTTPException(
            status_code=409,
            detail="Una regla aprobada solo puede pasar a 'retired' con registro de la razon.",
        )
    rule.status = "retired"
    session.add(rule)
    session.add(
        AuditLog(actor=f"user:{user.id}", entity="clinical_rule", entity_id=rule.id, action="retired")
    )
    session.commit()
    return {"rule_id": rule.id, "status": rule.status}
