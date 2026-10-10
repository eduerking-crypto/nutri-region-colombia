"""Configuracion central via variables de entorno."""
from __future__ import annotations

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]


def _env_bool(name: str, default: bool) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "si", "yes", "on"}


def load_dotenv_if_present() -> None:
    env_path = BASE_DIR / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8-sig").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip())


load_dotenv_if_present()


DB_URL: str = os.environ.get("NUTRI_DB_URL", f"sqlite:///{BASE_DIR / 'nutriregion.db'}")
JWT_SECRET: str = os.environ.get("NUTRI_JWT_SECRET", "dev-secret-no-usar-en-produccion")
JWT_EXPIRATION_HOURS: int = int(os.environ.get("NUTRI_JWT_EXPIRATION_HOURS", "24"))
RULES_PILOT_MODE: bool = _env_bool("NUTRI_RULES_PILOT_MODE", False)
AUTOSEED: bool = _env_bool("NUTRI_AUTOSEED", False)
AI_ENABLED: bool = _env_bool("NUTRI_AI_ENABLED", False)
OLLAMA_BASE_URL: str = os.environ.get("NUTRI_OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL: str = os.environ.get("NUTRI_OLLAMA_MODEL", "qwen3.5:4b")
ADMIN_EMAIL: str = os.environ.get("NUTRI_ADMIN_EMAIL", "admin@nutriregion.local")
ADMIN_PASSWORD: str = os.environ.get("NUTRI_ADMIN_PASSWORD", "nutri-admin-dev")

# Directorios de datos del repositorio
DATA_DIR = BASE_DIR.parent / "data"
IMPORTS_DIR = DATA_DIR / "imports"
FDC_RAW_DIR = IMPORTS_DIR / "fdc" / "raw"
FDC_NORMALIZED = IMPORTS_DIR / "fdc" / "normalized.json"
