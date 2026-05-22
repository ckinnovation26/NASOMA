"""Gestion JWT RS256 (clés asymétriques) et signature des codes de recharge.

Cf. §26 du Business Plan : "JWT signés avec clé asymétrique RS256,
rotation tous les 90 jours."
"""

import hashlib
import hmac
import secrets
from datetime import UTC, datetime, timedelta
from functools import lru_cache
from pathlib import Path
from typing import Any

from jose import jwt

from app.core.config import settings


# ──────────────────────────────────────────────
#  Chargement des clés RS256
# ──────────────────────────────────────────────
@lru_cache(maxsize=1)
def _load_private_key() -> str:
    """Charge la clé privée RSA depuis le filesystem (dev) ou Secret Manager (prod)."""
    return Path(settings.jwt_private_key_path).read_text(encoding="utf-8")


@lru_cache(maxsize=1)
def _load_public_key() -> str:
    """Charge la clé publique RSA."""
    return Path(settings.jwt_public_key_path).read_text(encoding="utf-8")


# ──────────────────────────────────────────────
#  JWT — Access & Refresh tokens
# ──────────────────────────────────────────────
def create_access_token(
    subject: str,
    extra_claims: dict[str, Any] | None = None,
) -> str:
    """Génère un JWT access signé RS256 (TTL 24h cf. §26 BP)."""
    expire = datetime.now(UTC) + timedelta(minutes=settings.jwt_access_token_ttl_minutes)
    payload: dict[str, Any] = {
        "sub": subject,
        "exp": expire,
        "iat": datetime.now(UTC),
        "type": "access",
    }
    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(
        payload,
        _load_private_key(),
        algorithm=settings.jwt_algorithm,
        headers={"kid": settings.jwt_key_id},
    )


def create_refresh_token(subject: str) -> str:
    """Génère un JWT refresh signé RS256 (TTL 30 jours)."""
    expire = datetime.now(UTC) + timedelta(days=settings.jwt_refresh_token_ttl_days)
    payload: dict[str, Any] = {
        "sub": subject,
        "exp": expire,
        "iat": datetime.now(UTC),
        "type": "refresh",
        "jti": secrets.token_hex(16),       # pour révocation
    }
    return jwt.encode(
        payload,
        _load_private_key(),
        algorithm=settings.jwt_algorithm,
        headers={"kid": settings.jwt_key_id},
    )


def decode_token(token: str) -> dict[str, Any]:
    """Décode et valide un JWT — lève JWTError si invalide."""
    return jwt.decode(
        token,
        _load_public_key(),
        algorithms=[settings.jwt_algorithm],
    )


# ──────────────────────────────────────────────
#  OTP — génération + hashing constant-time
# ──────────────────────────────────────────────
def generate_otp() -> str:
    """Génère un OTP numérique de longueur configurée (default 6)."""
    return "".join(secrets.choice("0123456789") for _ in range(settings.jwt_otp_length))


def hash_otp(code: str) -> str:
    """Hash SHA-256 d'un OTP (jamais stocker en clair, cf. table otp_challenges)."""
    return hashlib.sha256(code.encode()).hexdigest()


def verify_otp(code: str, stored_hash: str) -> bool:
    """Comparaison constant-time pour résister aux timing attacks."""
    return hmac.compare_digest(hash_otp(code), stored_hash)


# ──────────────────────────────────────────────
#  Tickets de recharge HMAC (16 chars NSMA-XXXX-XXXX-XXXX)
# ──────────────────────────────────────────────
def generate_recharge_code(plan: str, batch_id: str) -> tuple[str, str]:
    """Génère un code de recharge + HMAC signature."""
    payload = secrets.token_hex(6).upper()
    code = f"NSMA-{payload[0:4]}-{payload[4:8]}-{payload[8:12]}"
    signature = hmac.new(
        settings.payment_ticket_hmac_secret.encode(),
        f"{code}|{plan}|{batch_id}".encode(),
        hashlib.sha256,
    ).hexdigest()
    return code, signature


def verify_recharge_code(code: str, plan: str, batch_id: str, signature: str) -> bool:
    """Vérifie qu'un code de recharge est authentique."""
    expected = hmac.new(
        settings.payment_ticket_hmac_secret.encode(),
        f"{code}|{plan}|{batch_id}".encode(),
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected, signature)
