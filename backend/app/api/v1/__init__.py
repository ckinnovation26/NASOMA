"""API v1 — agrégation des sous-routeurs."""

from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.billing import router as billing_router
from app.api.v1.communications import router as communications_router
from app.api.v1.customer_signup import router as customer_signup_router
from app.api.v1.fallback import router as fallback_router
from app.api.v1.indicators import router as indicators_router
from app.api.v1.payments import router as payments_router
from app.api.v1.reviews import router as reviews_router
from app.api.v1.scans import router as scans_router
from app.api.v1.sessions import router as sessions_router

router = APIRouter()


@router.get("/", tags=["meta"])
async def api_root() -> dict[str, str]:
    return {
        "api": "nasoma",
        "version": "v1",
        "status": "sprint-5-complete",
    }


router.include_router(auth_router, prefix="/auth", tags=["auth"])
router.include_router(customer_signup_router, tags=["customer-signup"])
router.include_router(scans_router, prefix="/scans", tags=["scans"])
router.include_router(sessions_router, prefix="/sessions", tags=["sessions"])
router.include_router(fallback_router, tags=["fallback"])
router.include_router(billing_router, tags=["billing"])
router.include_router(payments_router, prefix="/payments", tags=["payments"])
router.include_router(indicators_router, tags=["indicators"])
router.include_router(reviews_router, tags=["spaced-repetition"])
router.include_router(communications_router, tags=["communications"])
