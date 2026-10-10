"""Reglas clinicas versionadas.

ADR-0004: las reglas son DATOS versionados. El motor solo aplica reglas con
status=approved; en modo piloto (desarrollo) puede evaluar candidatas con un
banner visible en la UI. Ver docs/adr/ADR-0004.
"""
import json
from datetime import date, datetime

from sqlmodel import Field, SQLModel


class ClinicalRule(SQLModel, table=True):
    __tablename__ = "clinical_rules"

    id: str = Field(primary_key=True)
    version: int = 1
    scope: str = Field(index=True)
    name: str
    conditions: str = "[]"  # JSON: lista de condiciones (todas deben cumplirse)
    exceptions: str = "[]"
    action: str  # bloquear | derivar_profesional | derivar_urgencia | advertir
    message: str
    justification: str
    source_desc: str
    evidence_level: str = "pendiente_verificacion"
    status: str = Field(default="candidate", index=True)
    reviewer: str | None = None
    approved_at: datetime | None = None
    next_review: date | None = None

    @property
    def conditions_list(self) -> list[dict]:
        try:
            return json.loads(self.conditions)
        except json.JSONDecodeError:
            return []

    @property
    def exceptions_list(self) -> list[dict]:
        try:
            return json.loads(self.exceptions)
        except json.JSONDecodeError:
            return []
