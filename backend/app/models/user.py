"""Modelos de usuarios y datos personales (esquema segregado del catalogo)."""
import json
from datetime import UTC, date, datetime

from sqlmodel import Field, Relationship, SQLModel

from app.models.catalog import jloads


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    password_hash: str
    role: str = Field(default="usuario", index=True)  # usuario | profesional | admin
    display_name: str | None = None
    consent_version: str | None = None
    consent_at: datetime | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    profile: UserProfile = Relationship(back_populates="user")


class UserProfile(SQLModel, table=True):
    __tablename__ = "user_profiles"

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(unique=True, foreign_key="users.id")
    department: str | None = None
    municipality: str | None = None
    zone: str | None = None  # urbana | rural
    household_size: int = 1
    budget_weekly_cop: float | None = None
    cooking_time_minutes: int | None = None
    has_refrigeration: bool = True
    meals_per_day: int = 3
    dietary_pattern: str = "omnivoro"  # omnivoro | vegetariano | vegano
    preferred_foods: str = "[]"
    rejected_foods: str = "[]"
    onboarding_completed: bool = False

    user: User | None = Relationship(back_populates="profile")

    @property
    def preferred_list(self) -> list[str]:
        return jloads(self.preferred_foods)

    @property
    def rejected_list(self) -> list[str]:
        return jloads(self.rejected_foods)


class UserAllergy(SQLModel, table=True):
    __tablename__ = "user_allergies"

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    allergen: str
    kind: str = "alergia_confirmada"  # alergia_confirmada | intolerancia | reaccion_conocida
    severity: str = "desconocida"  # alta | media | baja | desconocida
    notes: str | None = None


class UserHealthFlag(SQLModel, table=True):
    __tablename__ = "user_health_flags"

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    flag: str  # diabetes_medicamentos | enfermedad_renal | embarazo | lactancia | posible_tca | perdida_peso_involuntaria | sintomas_alarma
    self_reported: bool = True
    notes: str | None = None


class MenuPlan(SQLModel, table=True):
    __tablename__ = "menu_plans"

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    days: str = "[]"  # JSON: estructura del menu
    status: str = "activo"  # borrador | activo | pendiente_revision | aprobado | rechazado
    warnings: str = "[]"
    applied_rules: str = "[]"
    triage_result: str | None = None
    reviewer_id: int | None = Field(default=None, foreign_key="users.id")
    review_notes: str | None = None
    reviewed_at: datetime | None = None

    @property
    def days_list(self) -> list:
        return json.loads(self.days) if self.days else []

    @property
    def warnings_list(self) -> list[str]:
        return json.loads(self.warnings) if self.warnings else []


class TrackingEntry(SQLModel, table=True):
    __tablename__ = "tracking_entries"

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    entry_date: date = Field(index=True)
    kind: str = "consumo"  # consumo | habito
    content: str = "{}"  # JSON libre minimo
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @property
    def content_dict(self) -> dict:
        try:
            return json.loads(self.content)
        except json.JSONDecodeError:
            return {}


class AuditLog(SQLModel, table=True):
    __tablename__ = "audit_log"

    id: int | None = Field(default=None, primary_key=True)
    at: datetime = Field(default_factory=lambda: datetime.now(UTC), index=True)
    actor: str
    entity: str = Field(index=True)
    entity_id: str
    action: str
    details: str | None = None
