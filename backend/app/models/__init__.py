"""Modèles SQLAlchemy — voir alembic/versions/ pour les migrations.

⚠️ Tous les modèles avec PII utilisateur incluent `tenant_id` pour multi-tenant
(cf. §20 BP). En MVP, un seul tenant 'KM' (Comores) en base.
"""

from app.models.billing import (
    BillKind,
    BillStatus,
    OutstandingBill,
    VideoAssistanceSession,
    VideoAssistanceStatus,
)
from app.models.communications import (
    ConversationStatus,
    MarketingAudience,
    MarketingMessage,
    MessageSender,
    SupportConversation,
    SupportMessage,
)
from app.models.concepts import Concept, ConceptPrerequisite
from app.models.identity import DocumentType, IdentityDocument, KycStatus
from app.models.indicators import IndicatorHorizon, MasterySnapshot, StudentIndicators
from app.models.fallback import (
    AssistanceReason,
    AssistanceStatus,
    FallbackContext,
    VendorAssistanceRequest,
)
from app.models.mastery import StudentConceptMastery
from app.models.otp_challenges import OtpChallenge, OtpStatus, OtpType
from app.models.payments import Payment, PaymentProvider, PaymentStatus
from app.models.recharge_tickets import RechargeTicket, TicketStatus
from app.models.spaced_repetition import (
    SR_INTERVALS_DAYS,
    ReviewOutcome,
    ReviewStatus,
    SpacedReview,
)
from app.models.scans import (
    DetectionType,
    Diagnostic,
    OcrProvider,
    Scan,
    ScanArchive,
    ScanStatus,
)
from app.models.sessions import (
    ExerciseTemplate,
    ExerciseType,
    Session,
    SessionAnswer,
    SessionStatus,
)
from app.models.subjects import Subject
from app.models.subscriptions import Subscription, SubscriptionPlan, SubscriptionStatus
from app.models.tenants import Tenant
from app.models.users import AccountState, SignupMethod, User, UserRole
from app.models.vendors import Vendor, VendorStatus, VendorType

__all__ = [
    "AccountState",
    "AssistanceReason",
    "AssistanceStatus",
    "BillKind",
    "BillStatus",
    "Concept",
    "ConceptPrerequisite",
    "ConversationStatus",
    "DetectionType",
    "Diagnostic",
    "ExerciseTemplate",
    "ExerciseType",
    "FallbackContext",
    "IdentityDocument",
    "IndicatorHorizon",
    "KycStatus",
    "MarketingAudience",
    "MarketingMessage",
    "MasterySnapshot",
    "MessageSender",
    "OcrProvider",
    "OutstandingBill",
    "OtpChallenge",
    "OtpStatus",
    "OtpType",
    "Payment",
    "PaymentProvider",
    "PaymentStatus",
    "RechargeTicket",
    "Scan",
    "ScanArchive",
    "ScanStatus",
    "ReviewOutcome",
    "ReviewStatus",
    "SpacedReview",
    "Session",
    "SessionAnswer",
    "SessionStatus",
    "SignupMethod",
    "StudentConceptMastery",
    "StudentIndicators",
    "Subject",
    "Subscription",
    "SubscriptionPlan",
    "SubscriptionStatus",
    "SupportConversation",
    "SupportMessage",
    "Tenant",
    "TicketStatus",
    "User",
    "UserRole",
    "Vendor",
    "VendorAssistanceRequest",
    "VendorStatus",
    "VendorType",
    "VideoAssistanceSession",
    "VideoAssistanceStatus",
]
