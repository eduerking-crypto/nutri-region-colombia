"""Aplicacion FastAPI de NutriRegion Colombia."""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import config, seed
from app.api import (
    admin,
    ai,
    auth,
    budget,
    evidence,
    foods,
    planner,
    professional,
    profile,
)
from app.api import (
    settings as settings_router,
)
from app.db import init_db


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    if config.AUTOSEED:
        seed.run()
    yield


app = FastAPI(
    title="NutriRegion Colombia API",
    version="0.1.0",
    description=(
        "Plataforma de nutricion territorial. Todo dato cientifico expone "
        "capa de confianza (medido/estimado/literatura/educativo), fuente y fecha."
    ),
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(foods.router, prefix="/api")
app.include_router(profile.router, prefix="/api")
app.include_router(planner.router, prefix="/api")
app.include_router(budget.router, prefix="/api")
app.include_router(evidence.router, prefix="/api")
app.include_router(professional.router, prefix="/api")
app.include_router(admin.router, prefix="/api")
app.include_router(settings_router.router, prefix="/api")
app.include_router(ai.router, prefix="/api")


@app.get("/api/salud")
def salud() -> dict:
    return {
        "status": "ok",
        "version": "0.1.0",
        "pilot_mode": config.RULES_PILOT_MODE,
        "ai_enabled": config.AI_ENABLED,
    }
