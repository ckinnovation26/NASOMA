"""Service Marketing + SAV — bot Gemini IA pour tous, humain ACTIVE only."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

import structlog
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.communications import (
    ConversationStatus,
    MarketingAudience,
    MarketingMessage,
    MessageSender,
    SupportConversation,
    SupportMessage,
)
from app.models.users import AccountState, User

logger = structlog.get_logger(__name__)


class SupportError(Exception):
    """Erreur métier support."""


class HumanEscalationRefusedError(SupportError):
    """Refusé : seulement les comptes ACTIVE peuvent demander un humain."""


class MarketingService:
    """Gère le feed marketing (visible tous états)."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_feed_for_user(
        self, user: User, max_items: int = 10
    ) -> list[MarketingMessage]:
        """Retourne les messages actifs pertinents pour l'état du user."""
        now = datetime.now(UTC)
        state_str = (
            user.account_state.value
            if hasattr(user.account_state, "value")
            else str(user.account_state)
        )

        # Construire la liste d'audiences ciblées qui matchent ce user
        audiences = [MarketingAudience.ALL]
        if user.account_state == AccountState.ACTIVE:
            audiences.append(MarketingAudience.ACTIVE)
        else:
            audiences.append(MarketingAudience.INACTIVE)
            if user.account_state == AccountState.GRACE:
                audiences.append(MarketingAudience.GRACE)
            elif user.account_state == AccountState.FROZEN:
                audiences.append(MarketingAudience.FROZEN)

        stmt = (
            select(MarketingMessage)
            .where(
                MarketingMessage.tenant_id == user.tenant_id,
                MarketingMessage.audience.in_(audiences),
                MarketingMessage.starts_at <= now,
                or_(
                    MarketingMessage.ends_at.is_(None),
                    MarketingMessage.ends_at > now,
                ),
            )
            .order_by(
                MarketingMessage.priority.asc(),
                MarketingMessage.created_at.desc(),
            )
            .limit(max_items)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())


class SupportService:
    """Gère les conversations SAV avec routing IA / humain."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def open_conversation(self, user: User) -> SupportConversation:
        """Ouvre une conversation SAV. Démarre en AI_ONLY."""
        state_str = (
            user.account_state.value
            if hasattr(user.account_state, "value")
            else str(user.account_state)
        )
        conv = SupportConversation(
            tenant_id=user.tenant_id,
            user_id=user.id,
            status=ConversationStatus.AI_ONLY,
            user_account_state_snapshot=state_str,
        )
        self.db.add(conv)
        await self.db.flush()
        logger.info("support.opened", conv_id=str(conv.id), user_id=str(user.id), state=state_str)
        return conv

    async def post_user_message(
        self, conversation_id: uuid.UUID, user: User, content: str
    ) -> SupportMessage:
        """Le user envoie un message. L'IA répond automatiquement (puis re-poll)."""
        conv = await self.db.get(SupportConversation, conversation_id)
        if conv is None or conv.user_id != user.id:
            raise SupportError("Conversation introuvable.")
        if conv.status == ConversationStatus.CLOSED:
            raise SupportError("Conversation fermée.")

        msg = SupportMessage(
            conversation_id=conversation_id,
            sender_type=MessageSender.USER,
            sender_id=user.id,
            content=content,
        )
        self.db.add(msg)
        await self.db.flush()

        # IA répond automatiquement si pas d'humain en charge
        if conv.status in (ConversationStatus.AI_ONLY, ConversationStatus.AWAITING_HUMAN):
            await self._ai_respond(conv, user, content)

        return msg

    async def request_human_escalation(
        self, conversation_id: uuid.UUID, user: User
    ) -> SupportConversation:
        """Le user demande de parler à un humain.

        - ACTIVE → status passe à AWAITING_HUMAN, ticket créé pour agents
        - Sinon → 402 + message "Réactivez votre abonnement"
        """
        conv = await self.db.get(SupportConversation, conversation_id)
        if conv is None or conv.user_id != user.id:
            raise SupportError("Conversation introuvable.")

        if user.account_state != AccountState.ACTIVE:
            # Log + refus + message IA proposant la réactivation
            ai_msg = SupportMessage(
                conversation_id=conversation_id,
                sender_type=MessageSender.AI,
                sender_id=None,
                content=(
                    "Désolé, l'assistance humaine est réservée aux abonnés actifs. "
                    "Pour parler à un agent, réactive ton abonnement chez un vendeur. "
                    "En attendant, je peux t'aider avec : la FAQ, comment recharger, "
                    "comment réactiver ton compte."
                ),
                ai_cost_usd=0.0001,
            )
            self.db.add(ai_msg)
            await self.db.flush()
            logger.info(
                "support.escalation_refused",
                conv_id=str(conversation_id),
                user_state=user.account_state.value,
            )
            raise HumanEscalationRefusedError(
                "Assistance humaine réservée aux abonnés actifs."
            )

        conv.status = ConversationStatus.AWAITING_HUMAN
        await self.db.flush()
        logger.info("support.escalated", conv_id=str(conversation_id))
        return conv

    async def close_conversation(
        self,
        conversation_id: uuid.UUID,
        user: User,
        satisfaction_rating: int | None = None,
    ) -> SupportConversation:
        conv = await self.db.get(SupportConversation, conversation_id)
        if conv is None or conv.user_id != user.id:
            raise SupportError("Conversation introuvable.")
        conv.status = ConversationStatus.CLOSED
        conv.closed_at = datetime.now(UTC)
        if satisfaction_rating and 1 <= satisfaction_rating <= 5:
            conv.satisfaction_rating = satisfaction_rating
        await self.db.flush()
        return conv

    async def get_messages(
        self, conversation_id: uuid.UUID, user: User
    ) -> list[SupportMessage]:
        conv = await self.db.get(SupportConversation, conversation_id)
        if conv is None or conv.user_id != user.id:
            raise SupportError("Conversation introuvable.")
        stmt = (
            select(SupportMessage)
            .where(SupportMessage.conversation_id == conversation_id)
            .order_by(SupportMessage.created_at.asc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    # ──────────────────────────────────────────────
    #  IA bot — stub Sprint 5, Gemini réel Sprint 6
    # ──────────────────────────────────────────────
    async def _ai_respond(
        self, conv: SupportConversation, user: User, user_msg: str
    ) -> SupportMessage:
        """Génère une réponse IA via Gemini Flash.

        Sprint 5 : stub avec réponses pré-câblées par keyword.
        Sprint 6 : vrai appel Gemini avec system prompt + context account_state.
        """
        response = self._stub_response(user, user_msg)

        ai_msg = SupportMessage(
            conversation_id=conv.id,
            sender_type=MessageSender.AI,
            sender_id=None,
            content=response,
            ai_cost_usd=0.0002,
        )
        self.db.add(ai_msg)
        await self.db.flush()
        return ai_msg

    def _stub_response(self, user: User, user_msg: str) -> str:
        """Réponses IA stub par mot-clé pour MVP."""
        msg_lower = user_msg.lower()
        active = user.account_state == AccountState.ACTIVE

        if any(k in msg_lower for k in ["recharge", "recharger", "ticket", "payer"]):
            return (
                "Pour recharger ton compte Nasoma, va voir un vendeur Nasoma près de chez toi. "
                "Le vendeur te donnera un ticket avec un code OTP à entrer dans l'app. "
                "Tu peux aussi demander à un proche en France/Émirats de payer pour toi via notre site web."
            )
        if any(k in msg_lower for k in ["scan", "scanner", "photo", "caméra", "camera"]):
            return (
                "Pour scanner une copie : ouvre l'app → bouton caméra → pose la feuille bien à plat, "
                "éclairage suffisant, cadre la feuille entière. Si l'image est floue, "
                "tu peux reprendre la photo gratuitement dans les 5 minutes."
            )
        if any(k in msg_lower for k in ["whatsapp", "code", "otp", "activation"]):
            return (
                "Le code OTP est envoyé via WhatsApp au numéro que tu as déclaré. "
                "Si tu ne le reçois pas, vérifie : WhatsApp installé, bon numéro, connexion internet. "
                "Le code expire après 5 minutes — demande un nouveau code si besoin."
            )
        if any(k in msg_lower for k in ["bloqué", "ne marche pas", "problème", "bug"]):
            if active:
                return (
                    "Je vais essayer de t'aider. Peux-tu me préciser : à quelle étape ça bloque ? "
                    "Quel message d'erreur as-tu vu ? Si je ne peux pas résoudre, je peux te mettre "
                    "en contact avec un agent humain (tape « parler à un humain »)."
                )
            return (
                "Je vais essayer de t'aider. Décris-moi le problème. "
                "(Note : l'assistance humaine est réservée aux abonnés actifs.)"
            )
        if any(k in msg_lower for k in ["humain", "agent", "personne"]):
            if active:
                return (
                    "Tu peux demander un agent humain en cliquant sur « Parler à un humain » "
                    "(bouton en bas de l'écran). Un agent te répond sous 24h."
                )
            return (
                "L'assistance humaine est réservée aux abonnés actifs. "
                "Pour y accéder, recharge ton compte chez un vendeur. "
                "En attendant, je peux répondre à beaucoup de questions — pose-les moi."
            )

        return (
            "Bonjour ! Je suis Mimi, l'assistant Nasoma. "
            "Comment puis-je t'aider ? Tu peux me poser des questions sur : "
            "le scan, la recharge, l'activation, les exercices, ton compte."
        )
