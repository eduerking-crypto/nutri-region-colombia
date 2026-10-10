"""Tokens JWT (HS256) con PyJWT."""
from __future__ import annotations

from datetime import UTC, datetime, timedelta

import jwt

from app import config


def create_token(user_id: int, role: str) -> str:
    payload = {
        "sub": str(user_id),
        "role": role,
        "iat": datetime.now(UTC),
        "exp": datetime.now(UTC) + timedelta(hours=config.JWT_EXPIRATION_HOURS),
    }
    return jwt.encode(payload, config.JWT_SECRET, algorithm="HS256")


def decode_token(token: str) -> dict:
    """Levanta jwt.InvalidTokenError si el token es invalido o expiro."""
    return jwt.decode(token, config.JWT_SECRET, algorithms=["HS256"])
