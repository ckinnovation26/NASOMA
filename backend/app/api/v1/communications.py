"""Endpoints marketing in-app + SAV 2 tiers."""

from __future__ import annotations

import uuid
from datetime import datetime

import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.users import User
from app.services.communications_service import (
    HumanEscalationRefusedError,
    MarketingService,
    SupportError,
    SupportService,
)

logger = structlog.get_logger(__name__)

router = APIRouter()


# ──────────────────────────────────────────────
#  Schemas
# ──────────────────────────────────────────────
class MarketingFeedItem(BaseModel):
    id: uuid.UUID
    title: str
    body: str
    cta_label: str | None
    cta_url: str | None
    priority: int
    starts_at: datetime
    ends_at: datetime | None


class MarketingFeedResponse(BaseModel):
    user_id: uuid.UUID
    items: list[MarketingFeedItem]


class OpenConversationPayload(BaseModel):
    user_id: uuid.UUID


class ConversationPublic(BaseModel):
    id: uuid.UUID
    status: str
    opened_at: datetime
    closed_at: datetime | None
    user_account_state_snapshot: str


class PostMessagePayload(BaseModel):
    user_id: uuid.UUID
    content: str = Field(..., min_length=1, max_length=2000)


class MessagePublic(BaseModel):
    id: uuid.UUID
    sender_type: str
    content: str
    created_at: datetime


class EscalatePayload(BaseModel):
    user_id: uuid.UUID


class ClosePayload(BaseModel):
    user_id: uuid.UUID
    satisfaction_rating: int | None = Field(default=None, ge=1, le=5)


# ──────────────────────────────────────────────
#  Marketing feed
# ──────────────────────────────────────────────
@router.get(
    "/marketing/feed",
    response_model=MarketingFeedResponse,
    summary="Feed marketing in-app (visible TOUS états même frozen)",
)
async def get_marketing_feed(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> MarketingFeedResponse:
    user = await db.get(User, user_id)
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User introuvable.")
    svc = MarketingService(db)
    items = await svc.get_feed_for_user(user)
    return MarketingFeedResponse(
        user_id=user_id,
        items=[
            MarketingFeedItem(
                id=m.id,
                title=m.title,
                body=m.body,
                cta_label=m.cta_label,
                cta_url=m.cta_url,
                priority=m.priority,
                starts_at=m.starts_at,
                ends_at=m.ends_at,
            )
            for m in items
        ],
    )


# ──────────────────────────────────────────────
#  Support conversations
# ──────────────────────────────────────────────
@router.post(
    "/support/conversations",
    response_model=ConversationPublic,
    status_code=status.HTTP_201_CREATED,
    summary="Ouvrir une conversation SAV (IA répond automatiquement)",
)
async def open_conversation(
    payload: OpenConversationPayload,
    db: AsyncSession = Depends(get_db),
) -> ConversationPublic:
    user = await db.get(User, payload.user_id)
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User introuvable.")
    svc = SupportService(db)
    conv = await svc.open_conversation(user)
    await db.commit()
    return ConversationPublic(
        id=conv.id,
        status=conv.status.value if hasattr(conv.status, "value") else str(conv.status),
        opened_at=conv.opened_at,
        closed_at=conv.closed_at,
        user_account_state_snapshot=conv.user_account_state_snapshot,
    )


@router.post(
    "/support/conversations/{conversation_id}/messages",
    response_model=MessagePublic,
    status_code=status.HTTP_201_CREATED,
    summary="Envoyer un message (IA répond auto si pas d'humain en charge)",
)
async def post_message(
    conversation_id: uuid.UUID,
    payload: PostMessagePayload,
    db: AsyncSession = Depends(get_db),
) -> MessagePublic:
    user = await db.get(User, payload.user_id)
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User introuvable.")
    svc = SupportService(db)
    try:
        msg = await svc.post_user_message(conversation_id, user, payload.content)
    except SupportError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e)) from e
    await db.commit()
    return MessagePublic(
        id=msg.id,
        sender_type=msg.sender_type.value
        if hasattr(msg.sender_type, "value")
        else str(msg.sender_type),
        content=msg.content,
        created_at=msg.created_at,
    )


@router.get(
    "/support/conversations/{conversation_id}/messages",
    response_model=list[MessagePublic],
    summary="Récupérer tous les messages d'une conversation",
)
async def get_messages(
    conversation_id: uuid.UUID,
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> list[MessagePublic]:
    user = await db.get(User, user_id)
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User introuvable.")
    svc = SupportService(db)
    try:
        msgs = await svc.get_messages(conversation_id, user)
    except SupportError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(e)) from e
    return [
        MessagePublic(
            id=m.id,
            sender_type=m.sender_type.value
            if hasattr(m.sender_type, "value")
            else str(m.sender_type),
            content=m.content,
            created_at=m.created_at,
        )
        for m in msgs
    ]


@router.post(
    "/support/conversations/{conversation_id}/escalate",
    response_model=ConversationPublic,
    summary="Demander un agent humain (refusé si compte non-ACTIVE)",
)
async def escalate(
    conversation_id: uuid.UUID,
    payload: EscalatePayload,
    db: AsyncSession = Depends(get_db),
) -> ConversationPublic:
    user = await db.get(User, payload.user_id)
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User introuvable.")
    svc = SupportService(db)
    try:
        conv = await svc.request_human_escalation(conversation_id, user)
    except HumanEscalationRefusedError as e:
        await db.commit()
        raise HTTPException(status.HTTP_402_PAYMENT_REQUIRED, str(e)) from e
    except SupportError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e)) from e
    await db.commit()
    return ConversationPublic(
        id=conv.id,
        status=conv.status.value if hasattr(conv.status, "value") else str(conv.status),
        opened_at=conv.opened_at,
        closed_at=conv.closed_at,
        user_account_state_snapshot=conv.user_account_state_snapshot,
    )


@router.post(
    "/support/conversations/{conversation_id}/close",
    response_model=ConversationPublic,
    summary="Fermer une conversation (avec note satisfaction optionnelle)",
)
async def close_conversation(
    conversation_id: uuid.UUID,
    payload: ClosePayload,
    db: AsyncSession = Depends(get_db),
) -> ConversationPublic:
    user = await db.get(User, payload.user_id)
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User introuvable.")
    svc = SupportService(db)
    try:
        conv = await svc.close_conversation(
            conversation_id, user, payload.satisfaction_rating
        )
    except SupportError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e)) from e
    await db.commit()
    return ConversationPublic(
        id=conv.id,
        status=conv.status.value if hasattr(conv.status, "value") else str(conv.status),
        opened_at=conv.opened_at,
        closed_at=conv.closed_at,
        user_account_state_snapshot=conv.user_account_state_snapshot,
    )
