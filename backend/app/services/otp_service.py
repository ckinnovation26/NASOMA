"""Service OTP — génération, hash, vérification, rotation.

Un OTP a 3 fonctions simultanées :
  1. Mot de passe (combiné au phone identifiant)
  2. Preuve de paiement
  3. Token de session

Types :
  - SMS_FIRST_SIGNUP   : envoyé par SMS Firebase pour 1ère inscription
  - VENDOR_TICKET      : généré par vendeur, imprimé sur ticket physique
  - DIASPORA_PORTAL    : généré via portail web diaspora
  - RECOVERY           : généré sur demande (compte gelé)

Sécurité :
  - Hash SHA-256, comparaison constant-time (anti timing attack)
  - Max 3 tentatives par OTP (lockout après)
  - Expiration stricte (5 min SMS, 30j ticket vendeur)
  - Invalidation automatique des anciens OTP lors de la rotation
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

import structlog
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import generate_otp, hash_otp, verify_otp
from app.models.otp_challenges import OtpChallenge, OtpStatus, OtpType

logger = structlog.get_logger(__name__)


class OtpError(Exception):
    """Erreur métier OTP (max attempts, expired, invalid)."""


class OtpMaxAttemptsError(OtpError):
    pass


class OtpExpiredError(OtpError):
    pass


class OtpInvalidError(OtpError):
    pass


class OtpService:
    """Gère le cycle de vie complet des OTP."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create_sms_first_signup(
        self,
        tenant_id: uuid.UUID,
        phone: str,
        ip_address: str | None = None,
        device_id: str | None = None,
    ) -> tuple[OtpChallenge, str]:
        """Génère un OTP pour la 1ère inscription par SMS.

        Returns:
            (challenge persisté, code en clair à envoyer par SMS)
        """
        # Invalider tous les OTP SMS pending pour ce phone (anti-spam)
        await self._invalidate_pending_for_phone(phone, otp_type=OtpType.SMS_FIRST_SIGNUP)

        code = generate_otp()
        challenge = OtpChallenge(
            tenant_id=tenant_id,
            user_id=None,                                      # pas encore créé
            phone=phone,
            code_hash=hash_otp(code),
            otp_type=OtpType.SMS_FIRST_SIGNUP,
            status=OtpStatus.PENDING,
            expires_at=datetime.now(UTC) + timedelta(minutes=settings.jwt_otp_ttl_minutes),
            max_attempts=settings.jwt_otp_max_attempts,
            ip_address=ip_address,
            device_id=device_id,
        )
        self.db.add(challenge)
        await self.db.flush()

        logger.info(
            "otp.sms_first_signup.created",
            challenge_id=str(challenge.id),
            phone_suffix=phone[-4:],
        )
        return challenge, code

    async def create_vendor_ticket(
        self,
        tenant_id: uuid.UUID,
        phone: str,
        subscription_id: uuid.UUID,
        recharge_ticket_code: str,
        duration_days: int,
    ) -> tuple[OtpChallenge, str]:
        """Génère un OTP pour activation par ticket vendeur.

        L'OTP a la durée du crédit (24h / 7j / 30j selon plan) — c'est aussi
        le token de session.
        """
        await self._invalidate_pending_for_phone(phone, otp_type=OtpType.VENDOR_TICKET)

        code = generate_otp()
        challenge = OtpChallenge(
            tenant_id=tenant_id,
            user_id=None,                                      # lié après redeem
            phone=phone,
            code_hash=hash_otp(code),
            otp_type=OtpType.VENDOR_TICKET,
            status=OtpStatus.PENDING,
            subscription_id=subscription_id,
            recharge_ticket_code=recharge_ticket_code,
            expires_at=datetime.now(UTC) + timedelta(days=duration_days),
            max_attempts=10,                                   # plus souple pour ticket physique
        )
        self.db.add(challenge)
        await self.db.flush()

        logger.info(
            "otp.vendor_ticket.created",
            challenge_id=str(challenge.id),
            phone_suffix=phone[-4:],
            ticket=recharge_ticket_code,
        )
        return challenge, code

    async def verify_and_consume(
        self,
        phone: str,
        code: str,
        otp_type: OtpType | None = None,
    ) -> OtpChallenge:
        """Vérifie un OTP et le marque consommé.

        Raises:
            OtpInvalidError : code incorrect (incrémente attempts)
            OtpExpiredError : code expiré
            OtpMaxAttemptsError : trop de tentatives
        """
        # Récupérer l'OTP pending le plus récent pour ce phone
        stmt = select(OtpChallenge).where(
            OtpChallenge.phone == phone,
            OtpChallenge.status == OtpStatus.PENDING,
        )
        if otp_type:
            stmt = stmt.where(OtpChallenge.otp_type == otp_type)
        stmt = stmt.order_by(OtpChallenge.created_at.desc()).limit(1)

        result = await self.db.execute(stmt)
        challenge: OtpChallenge | None = result.scalar_one_or_none()

        if challenge is None:
            logger.warning("otp.verify.no_pending", phone_suffix=phone[-4:])
            raise OtpInvalidError("Aucun OTP en attente pour ce numéro.")

        # Expiration
        now = datetime.now(UTC)
        expires_at = challenge.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=UTC)
        if expires_at < now:
            challenge.status = OtpStatus.EXPIRED
            await self.db.flush()
            logger.warning("otp.verify.expired", challenge_id=str(challenge.id))
            raise OtpExpiredError("Code expiré.")

        # Max attempts
        if challenge.attempts >= challenge.max_attempts:
            challenge.status = OtpStatus.INVALIDATED
            await self.db.flush()
            logger.warning("otp.verify.max_attempts", challenge_id=str(challenge.id))
            raise OtpMaxAttemptsError("Trop de tentatives.")

        # Vérification du code
        if not verify_otp(code, challenge.code_hash):
            challenge.attempts += 1
            await self.db.flush()
            logger.warning(
                "otp.verify.invalid_code",
                challenge_id=str(challenge.id),
                attempt=challenge.attempts,
            )
            raise OtpInvalidError(
                f"Code incorrect. Tentative {challenge.attempts}/{challenge.max_attempts}."
            )

        # Succès — marquer consommé
        challenge.status = OtpStatus.CONSUMED
        challenge.consumed_at = now
        await self.db.flush()

        logger.info(
            "otp.verify.consumed",
            challenge_id=str(challenge.id),
            phone_suffix=phone[-4:],
            otp_type=challenge.otp_type,
        )
        return challenge

    async def _invalidate_pending_for_phone(
        self,
        phone: str,
        otp_type: OtpType,
    ) -> int:
        """Invalide tous les OTP pending d'un type donné pour un phone.

        Mécanisme de rotation : un nouveau OTP rend les anciens caducs.
        """
        stmt = (
            update(OtpChallenge)
            .where(
                OtpChallenge.phone == phone,
                OtpChallenge.otp_type == otp_type,
                OtpChallenge.status == OtpStatus.PENDING,
            )
            .values(status=OtpStatus.INVALIDATED)
        )
        result = await self.db.execute(stmt)
        count = result.rowcount or 0
        if count:
            logger.info(
                "otp.rotated",
                phone_suffix=phone[-4:],
                otp_type=otp_type,
                invalidated_count=count,
            )
        return count

    async def cleanup_expired(self) -> int:
        """Cron utility : marque tous les OTP pending dont expires_at < NOW comme EXPIRED."""
        stmt = (
            update(OtpChallenge)
            .where(
                OtpChallenge.status == OtpStatus.PENDING,
                OtpChallenge.expires_at < datetime.now(UTC),
            )
            .values(status=OtpStatus.EXPIRED)
        )
        result = await self.db.execute(stmt)
        return result.rowcount or 0
