"""Biblioteca de fuentes, evidencia y reglas (transparencia del sistema)."""
from __future__ import annotations

from fastapi import APIRouter
from sqlmodel import select

from app import config
from app.api.deps import SessionDep
from app.models import ClinicalRule, Evidence, Source

router = APIRouter(prefix="/evidencia", tags=["evidencia"])


@router.get("/fuentes")
def fuentes(session: SessionDep) -> list[dict]:
    items = session.exec(select(Source)).all()
    return [
        {
            "id": item.id,
            "name": item.name,
            "kind": item.kind,
            "version": item.version,
            "license": item.license,
            "redistribution_allowed": item.redistribution_allowed,
            "access_method": item.access_method,
            "url": item.url,
            "citation": item.citation,
            "retrieved_at": str(item.retrieved_at),
            "notes": item.notes,
        }
        for item in sorted(items, key=lambda s: s.id)
    ]


@router.get("/referencias")
def referencias(session: SessionDep) -> list[dict]:
    items = session.exec(select(Evidence)).all()
    return [
        {
            "id": item.id,
            "title": item.title,
            "citation": item.citation,
            "doi": item.doi,
            "pmid": item.pmid,
            "stable_url": item.stable_url,
            "study_type": item.study_type,
            "relevant_finding": item.relevant_finding,
            "limitations": item.limitations,
            "trust_tier": item.trust_tier,
            "verification_status": item.verification_status,
            "reviewed_at": str(item.reviewed_at),
        }
        for item in sorted(items, key=lambda e: e.id)
    ]


@router.get("/reglas")
def reglas(session: SessionDep) -> list[dict]:
    """Catalogo publico de reglas con su estado y procedencia."""
    items = session.exec(select(ClinicalRule)).all()
    return [
        {
            "id": item.id,
            "version": item.version,
            "scope": item.scope,
            "name": item.name,
            "action": item.action,
            "message": item.message,
            "justification": item.justification,
            "source_desc": item.source_desc,
            "evidence_level": item.evidence_level,
            "status": item.status,
            "reviewer": item.reviewer,
            "approved_at": item.approved_at.isoformat() if item.approved_at else None,
            "pilot_mode": config.RULES_PILOT_MODE,
        }
        for item in sorted(items, key=lambda r: r.id)
    ]
