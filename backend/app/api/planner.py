"""Planificador: triage de seguridad + generacion determinista de menus."""
from __future__ import annotations

import json

from fastapi import APIRouter
from sqlmodel import select

from app import config
from app.api.deps import CurrentUser, SessionDep
from app.engine.calc import adequacy
from app.engine.optimize import (
    build_entries,
    generate_menu,
    menu_totals_per_day,
    shopping_list,
)
from app.engine.rules import load_active_rules
from app.engine.triage import build_context, evaluate_safety
from app.models import (
    Food,
    FoodNutrient,
    MenuPlan,
    UserAllergy,
    UserHealthFlag,
    UserProfile,
)
from app.models.catalog import jdumps
from app.schemas import MenuRequest, PlanOut

router = APIRouter(prefix="/planificador", tags=["planificador"])

LIMITACIONES = [
    "Composicion de ingredientes crudos: los cambios por coccion no estan incluidos "
    "salvo en los datos de origen.",
    "Porciones nominales del proyecto (educativo), ajustables por el usuario.",
    "Los costos se muestran solo con precios observados/publicados con fecha; "
    "sin datos se indica expresamente.",
]


@router.post("/generar", response_model=PlanOut)
def generar_menu(payload: MenuRequest, session: SessionDep, user: CurrentUser) -> PlanOut:
    profile = session.exec(
        select(UserProfile).where(UserProfile.user_id == user.id)
    ).first()
    allergies = session.exec(select(UserAllergy).where(UserAllergy.user_id == user.id)).all()
    flags = session.exec(select(UserHealthFlag).where(UserHealthFlag.user_id == user.id)).all()
    ctx = build_context(profile, allergies, flags)

    rules = load_active_rules(session, config.RULES_PILOT_MODE)
    foods = session.exec(select(Food)).all()
    safety = evaluate_safety(ctx, rules, available_foods=foods)

    plan = MenuPlan(user_id=user.id, triage_result=safety.status)
    plan.applied_rules = jdumps(safety.applied_rules)
    plan.warnings = jdumps([msg.message for msg in safety.messages])

    if safety.status in ("bloqueado", "urgencia", "requiere_profesional"):
        plan.days = jdumps([])
        plan.status = "pendiente_revision" if safety.status == "requiere_profesional" else "bloqueado"
        session.add(plan)
        session.commit()
        session.refresh(plan)
        return PlanOut(
            plan_id=plan.id,
            status=safety.status,
            safety_messages=[
                {"severity": msg.severity, "code": msg.code, "message": msg.message}
                for msg in safety.messages
            ],
            applied_rules=safety.applied_rules,
            menu=None,
            nutrition_per_day=None,
            adequacy=None,
            pilot_mode=config.RULES_PILOT_MODE,
            limitations=LIMITACIONES,
        )

    nutrients = session.exec(select(FoodNutrient)).all()
    entries = build_entries(foods, nutrients)
    rejected = set(profile.rejected_list) if profile else set()
    preferred = set(profile.preferred_list) if profile else set()
    meals = profile.meals_per_day if profile else 3

    menu, warnings = generate_menu(
        entries=entries,
        days=payload.days,
        meals_per_day=meals,
        pattern=ctx.dietary_pattern,
        excluded_ids=set(safety.excluded_food_ids),
        preferred_ids=preferred,
        rejected_ids=rejected,
    )
    totals = menu_totals_per_day(menu, entries)
    day_adequacy = [adequacy(day_totals) for day_totals in totals]

    shopping = shopping_list(menu)
    menu_con_lista = menu | {"lista_compras": shopping}
    plan.days = jdumps(menu_con_lista)
    plan.status = "activo"
    all_warnings = [msg.message for msg in safety.messages] + warnings
    plan.warnings = jdumps(all_warnings)
    session.add(plan)
    session.commit()
    session.refresh(plan)

    return PlanOut(
        plan_id=plan.id,
        status=safety.status,
        safety_messages=[
            {"severity": msg.severity, "code": msg.code, "message": msg.message}
            for msg in safety.messages
        ],
        applied_rules=safety.applied_rules,
        menu=menu_con_lista,
        nutrition_per_day={str(index + 1): value for index, value in enumerate(totals)},
        adequacy=day_adequacy[0] if day_adequacy else None,
        pilot_mode=config.RULES_PILOT_MODE,
        limitations=LIMITACIONES,
    )


@router.get("/historial")
def historial(session: SessionDep, user: CurrentUser) -> list[dict]:
    plans = session.exec(
        select(MenuPlan)
        .where(MenuPlan.user_id == user.id)
        .order_by(MenuPlan.created_at.desc())  # type: ignore[union-attr]
    ).all()
    return [
        {
            "plan_id": plan.id,
            "created_at": plan.created_at.isoformat(),
            "status": plan.status,
            "warnings": plan.warnings_list,
            "applied_rules": json.loads(plan.applied_rules or "[]"),
        }
        for plan in plans[:20]
    ]
