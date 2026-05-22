"""Configuration centralisée — chargée depuis les variables d'environnement."""

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Toutes les variables d'env. — lues depuis `.env` en dev, Secret Manager en prod."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ─── Application ───
    app_env: Literal["dev", "staging", "prod"] = "dev"
    app_name: str = "nasoma-backend"
    app_version: str = "0.1.0"
    log_level: str = "INFO"

    # ─── API ───
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_base_url: str = "http://localhost:8000"
    cors_origins: str = "http://localhost:3000"

    # ─── PostgreSQL ───
    database_url: str = Field(
        default="postgresql+asyncpg://nasoma:changeme_local_only@localhost:5432/nasoma"
    )

    # ─── Firestore / GCP ───
    firestore_project_id: str = "nasoma-dev"
    firestore_emulator_host: str | None = None
    gcp_project_id: str = "nasoma-dev"
    gcp_region: str = "africa-south1"
    gcp_storage_bucket: str = "nasoma-dev-scans"
    gcp_tasks_queue: str = "ocr-queue"
    google_application_credentials: str | None = None

    # ─── Firebase ───
    firebase_project_id: str = "nasoma-dev"

    # ─── IA — Vision ───
    vision_api_enabled: bool = True
    vision_api_daily_budget_usd: float = 10.0

    # ─── IA — Gemini ───
    gemini_api_key: str = ""
    gemini_model_extract: str = "gemini-2.0-flash"
    gemini_model_generate: str = "gemini-1.5-flash-8b"
    gemini_temperature_extract: float = 0.0
    gemini_temperature_generate: float = 0.2
    gemini_daily_budget_usd: float = 5.0

    # ─── JWT (RS256 asymétrique) ───
    jwt_algorithm: str = "RS256"
    jwt_private_key_path: str = "./secrets/jwt_private.pem"
    jwt_public_key_path: str = "./secrets/jwt_public.pem"
    jwt_key_id: str = "v1"
    jwt_access_token_ttl_minutes: int = 1440        # 24h (§26 BP)
    jwt_refresh_token_ttl_days: int = 30
    jwt_otp_length: int = 6
    jwt_otp_ttl_minutes: int = 5
    jwt_otp_max_attempts: int = 3

    # ─── SMS ───
    sms_provider: Literal["africastalking", "twilio"] = "africastalking"
    africastalking_username: str = "sandbox"
    africastalking_api_key: str = ""
    africastalking_sender_id: str = "NASOMA"
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_from_number: str = ""

    # ─── Paiement ───
    hollo_api_key: str = ""
    hollo_merchant_id: str = ""
    hollo_webhook_secret: str = ""
    payment_ticket_hmac_secret: str = "changeme"

    # ─── Quotas & anti-abus ───
    quota_free_trial_scans: int = 3                  # plan Découverte
    quota_free_trial_ttl_days: int = 7               # expiration découverte (push à l'action)
    quota_throttle_scans_per_hour: int = 20
    quota_phash_cache_ttl_hours: int = 24
    quota_max_upload_size_kb: int = 200
    quota_grace_period_days: int = 30                # lecture seule après expiration crédit
    quota_frozen_to_archived_days: int = 365         # archivage cold storage

    # ─── Fallback "Always Give Value" ───
    fallback_max_per_24h: int = 1                    # anti-abus images aléatoires
    fallback_confidence_threshold: float = 0.55      # < ce seuil OCR → fallback
    fallback_default_exercises_count: int = 3
    fallback_rescan_grace_minutes: int = 5           # re-scan gratuit dans les 5 min

    # ─── Assistance vidéo (post-paid 200 KMF / 10 min, ACTIVE only) ───
    video_assistance_rate_kmf_per_10min: int = 200
    video_assistance_min_billed_minutes: int = 1     # facturation minimale même < 10 min
    video_assistance_max_session_minutes: int = 120  # session bloquée au-delà
    video_assistance_disclosure_text: str = (
        "Cette assistance vidéo coûte 200 KMF par tranche de 10 minutes. "
        "Le montant sera facturé à votre prochaine recharge chez votre vendeur. "
        "En continuant, vous acceptez cette tarification."
    )

    # ─── Observabilité ───
    sentry_dsn: str = ""
    bigquery_dataset: str = "nasoma_analytics"
    enable_ai_cost_tracking: bool = True

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse la chaîne CORS_ORIGINS en liste."""
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def is_production(self) -> bool:
        return self.app_env == "prod"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Singleton — instancie une seule fois par process."""
    return Settings()


settings = get_settings()
