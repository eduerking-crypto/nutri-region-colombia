"""Motor y sesiones SQLAlchemy/SQLModel."""
from __future__ import annotations

from collections.abc import Iterator

from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app import config


def _build_engine(url: str):
    if url.startswith("sqlite"):
        # check_same_thread=False es necesario para FastAPI/pytest; el acceso
        # sigue estando serializado por el Session por peticion.
        kwargs = {"connect_args": {"check_same_thread": False}}
        if ":memory:" in url:
            kwargs["poolclass"] = StaticPool
        return create_engine(url, **kwargs)
    return create_engine(url)


engine = _build_engine(config.DB_URL)


def init_db() -> None:
    """Crea el esquema. En produccion las migraciones se hacen con Alembic."""
    import app.models  # noqa: F401  (registrar todos los modelos)

    try:
        SQLModel.metadata.create_all(engine)
    except Exception as error:  # noqa: BLE001
        from pathlib import Path

        log = Path(__file__).resolve().parents[1] / "init_db_error.log"
        log.write_text(f"DB_URL={config.DB_URL!r}\ncwd={Path.cwd()!r}\nerror={error!r}", encoding="utf-8")
        raise


def get_session() -> Iterator[Session]:
    with Session(engine) as session:
        yield session
