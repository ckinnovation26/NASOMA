"""Modèle IdentityDocument — KYC obligatoire au 1er achat.

Décision (2026-05-20) : seule source de vérité d'identité = pièce scannée
- Vendeur scanne CNI / passeport / acte de naissance lors du signup en personne
- Diaspora uploade les pièces lors du 1er achat (acte de naissance enfant + CNI parent)

Sans pièce, le compte est créé mais non vérifié (kyc_status = NOT_VERIFIED).
Les opérations sensibles (paiement diaspora, assistance vidéo) exigent KYC VERIFIED.
"""

from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import DateTime, Enum

from app.db.session import Base


class DocumentType(str, enum.Enum):
    CNI = "cni"                                  # Carte Nationale d'Identité
    PASSPORT = "passport"
    BIRTH_CERTIFICATE = "birth_certificate"      # Acte de naissance (mineurs)
    SCHOOL_CARD = "school_card"                  # Carte d'élève (fallback)


class KycStatus(str, enum.Enum):
    NOT_VERIFIED = "not_verified"                # pas de pièce uploadée
    PENDING = "pending"                          # uploadée, en attente review
    VERIFIED = "verified"                        # validée par vendeur ou admin
    REJECTED = "rejected"                        # incohérente (rare)


class IdentityDocument(Base):
    """Pièce d'identité scannée — preuve KYC.

    Stockage : Cloud Storage privé + chiffré (Cloud KMS AES-256-GCM).
    Conservation : 5 ans après dernier usage du compte (obligation légale OSI).
    """

    __tablename__ = "identity_documents"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    document_type: Mapped[DocumentType] = mapped_column(
        Enum(DocumentType),
        nullable=False,
    )
    # Stockage chiffré Cloud Storage
    image_storage_key: Mapped[str] = mapped_column(String(256), nullable=False)
    thumbnail_storage_key: Mapped[str | None] = mapped_column(String(256), nullable=True)

    # OCR pour BI (numéro de carte hashé, nom)
    extracted_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    extracted_document_number_hash: Mapped[str | None] = mapped_column(
        String(128), nullable=True
    )
    extracted_birth_date: Mapped[str | None] = mapped_column(String(10), nullable=True)

    # Validation
    uploaded_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
    )
    uploaded_by_source: Mapped[str] = mapped_column(String(40), nullable=False)
    # 'vendor_in_person' | 'diaspora_portal' | 'app_self_upload' | 'admin_manual'
    verified_by_vendor_code: Mapped[str | None] = mapped_column(String(40), nullable=True)
    verified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True,
    )
    rejection_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Status
    kyc_status: Mapped[KycStatus] = mapped_column(
        Enum(KycStatus),
        default=KycStatus.PENDING,
        nullable=False,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    def __repr__(self) -> str:
        return (
            f"<IdentityDocument {self.id} user={self.user_id} "
            f"type={self.document_type} kyc={self.kyc_status}>"
        )
