"""Dépendances FastAPI partagées — injection JWT, DB, etc."""

from __future__ import annotations

import uuid

import structlog
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_token
from app.db.session import get_db
from app.models.users import AccountState, User

logger = structlog.get_logger(__name__)

_bearer = HTTPBearer(auto_error=True)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Extrait et valide le JWT Bearer — retourne le User authentifié.

    Lève HTTP 401 si token absent, invalide ou expiré.
    Lève HTTP 403 si compte archivé (ne doit plus accéder à l'API).
    """
    token = credentials.credentials
    try:
        payload = decode_token(token)
    except JWTError as exc:
        logger.warning("auth.jwt.invalid", error=str(exc))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide ou expiré.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    token_type = payload.get("type")
    if token_type != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de type incorrect (attendu: access).",
            headers={"WWW-Authenticate": "Bearer"},
        )

    subject = payload.get("sub")
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token sans sujet.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_id = uuid.UUID(subject)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sujet du token malformé.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Utilisateur introuvable.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if user.account_state == AccountState.ARCHIVED:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Compte archivé.",
        )

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Comme get_current_user mais bloque aussi les comptes FROZEN."""
    if current_user.account_state == AccountState.FROZEN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Compte suspendu. Achetez un ticket chez un vendeur pour réactiver.",
        )
    return current_user
