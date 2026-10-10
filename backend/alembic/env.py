"""Configuracion de Alembic para NutriRegion Colombia.

La URL de conexion se toma de app.config (NUTRI_DB_URL), nunca hardcodeada.
Para el baseline se genero contra una BD vacia con:
    NUTRI_DB_URL=sqlite:///_baseline_tmp.db alembic revision --autogenerate
y el esquema existente de desarrollo se marco con `alembic stamp head`.
"""
from __future__ import annotations

import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlmodel import SQLModel

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import config  # noqa: E402
import app.models  # noqa: F401,E402

config_alembic = context.config
if config_alembic.config_file_name is not None:
    fileConfig(config_alembic.config_file_name)

config_alembic.set_main_option("sqlalchemy.url", config.DB_URL)
target_metadata = SQLModel.metadata


def run_migrations_offline() -> None:
    context.configure(
        url=config.DB_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    from sqlalchemy import create_engine

    connectable = create_engine(config.DB_URL, connect_args={"check_same_thread": False})
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
