"""Modèle Tenant — multi-tenant par pays (KM, KE, TZ, CD).

Cf. §20 BP : "Tenant = pays. Chaque tenant a son Knowledge Graph
(curriculum local) et sa configuration (langue, devise, gateway MoMo)."

MVP : un seul tenant 'KM' (Comores) en base, mais le schéma est prêt Y2.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import JSON, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import DateTime

from app.db.session import Base

if TYPE_CHECKING:
    from app.models.users import User


class Tenant(Base):
    __tablename__ = "tenants"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    code: Mapped[str] = mapped_column(String(8), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    default_locale: Mapped[str] = mapped_column(String(10), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    momo_providers: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    users: Mapped[list[User]] = relationship(back_populates="tenant")

    def __repr__(self) -> str:
        return f"<Tenant {self.code} {self.name}>"
