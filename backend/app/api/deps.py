"""Dependencias compartidas de la API: sesion, usuario actual, roles."""
from __future__ import annotations

from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Session

from app import config
from app.db import get_session
from app.models import User
from app.security.tokens import decode_token

bearer_scheme = HTTPBearer(auto_error=False)

SessionDep = Annotated[Session, Depends(get_session)]


def get_current_user(
    session: SessionDep,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)] = None,
) -> User:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Se requiere iniciar sesion.",
        )
    try:
        payload = decode_token(credentials.credentials)
    except jwt.InvalidTokenError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Sesion invalida o expirada."
        ) from error
    user = session.get(User, int(payload["sub"]))
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Cuenta inexistente.")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def get_optional_user(
    session: SessionDep,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)] = None,
) -> User | None:
    """Usuario autenticado o None (para endpoints publicos con personalizacion)."""
    if credentials is None:
        return None
    try:
        payload = decode_token(credentials.credentials)
    except jwt.InvalidTokenError:
        return None
    return session.get(User, int(payload["sub"]))


OptionalUser = Annotated[User | None, Depends(get_optional_user)]


def require_role(*roles: str):
    def _guard(user: CurrentUser) -> User:
        if user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para esta accion.",
            )
        return user

    return _guard


def pilot_mode_enabled() -> bool:
    return config.RULES_PILOT_MODE
