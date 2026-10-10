"""Autenticacion, consentimiento y estado del sistema."""
from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException, status
from sqlmodel import select

from app import config
from app.api.deps import CurrentUser, SessionDep
from app.models import ClinicalRule, Food, PriceObservation, Recipe, User, UserProfile
from app.schemas import EstadoOut, LoginIn, RegistroIn, TokenOut, UserOut
from app.security.passwords import hash_password, verify_password
from app.security.tokens import create_token

CONSENT_VERSION = "2026-10-v1"

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/registro", response_model=TokenOut, status_code=status.HTTP_201_CREATED)
def registro(payload: RegistroIn, session: SessionDep) -> TokenOut:
    if not payload.accept_consent:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="El consentimiento informado es obligatorio para crear la cuenta.",
        )
    existing = session.exec(select(User).where(User.email == payload.email)).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ese correo ya esta registrado.")
    user = User(
        email=payload.email,
        password_hash=hash_password(payload.password),
        display_name=payload.display_name,
        consent_version=CONSENT_VERSION,
        consent_at=datetime.now(UTC),
    )
    session.add(user)
    session.flush()
    session.add(UserProfile(user_id=user.id))
    session.commit()
    session.refresh(user)
    return TokenOut(
        access_token=create_token(user.id, user.role),
        role=user.role,
        display_name=user.display_name,
    )


@router.post("/login", response_model=TokenOut)
def login(payload: LoginIn, session: SessionDep) -> TokenOut:
    user = session.exec(select(User).where(User.email == payload.email)).first()
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Correo o contrasena incorrectos.")
    return TokenOut(
        access_token=create_token(user.id, user.role),
        role=user.role,
        display_name=user.display_name,
    )


@router.get("/me", response_model=UserOut)
def me(user: CurrentUser) -> UserOut:
    return UserOut(**user.model_dump())


@router.get("/estado", response_model=EstadoOut)
def estado(session: SessionDep) -> EstadoOut:
    """Estado publico del sistema: modo piloto, conteos reales."""
    rules = session.exec(select(ClinicalRule)).all()
    return EstadoOut(
        version="0.1.0-fase1-7",
        pilot_mode=config.RULES_PILOT_MODE,
        ai_enabled=config.AI_ENABLED,
        rules_total=len(rules),
        rules_approved=sum(1 for rule in rules if rule.status == "approved"),
        foods_total=len(session.exec(select(Food)).all()),
        recipes_total=len(session.exec(select(Recipe)).all()),
        prices_total=len(session.exec(select(PriceObservation)).all()),
    )


@router.post("/salir")
def salir() -> dict:
    """El token vive en el cliente; el 'cierre' es eliminarlo alli."""
    return {"mensaje": "Elimina el token de tu almacenamiento local para cerrar sesion."}
