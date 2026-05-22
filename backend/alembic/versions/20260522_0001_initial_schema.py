"""Initial schema — toutes les tables V1.0.

Revision ID: 20260522_0001
Revises    : —
Create Date: 2026-05-22

Note : cette migration crée le schéma complet via SQLAlchemy metadata.create_all().
Les migrations suivantes utiliseront alembic revision --autogenerate pour les diffs.
"""

from __future__ import annotations

from alembic import op

# revision identifiers
revision: str = "20260522_0001"
down_revision: str | None = None
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    # Importer tous les modèles pour enregistrer leurs tables dans Base.metadata
    from app.db.session import Base
    from app.models import *  # noqa: F401, F403

    bind = op.get_bind()
    Base.metadata.create_all(bind=bind)


def downgrade() -> None:
    from app.db.session import Base
    from app.models import *  # noqa: F401, F403

    bind = op.get_bind()
    Base.metadata.drop_all(bind=bind)
