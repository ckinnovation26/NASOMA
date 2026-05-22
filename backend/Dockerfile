# ════════════════════════════════════════════════════════════
#  Nasoma Backend — image multi-stage pour Cloud Run
# ════════════════════════════════════════════════════════════

# ──────────────────────────────────────────────
#  Stage 1 — Builder
# ──────────────────────────────────────────────
FROM python:3.12-slim AS builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /build

# Dépendances système pour compiler asyncpg, pillow, etc.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml ./
RUN pip install --upgrade pip && \
    pip install --user --no-warn-script-location .

# ──────────────────────────────────────────────
#  Stage 2 — Runtime
# ──────────────────────────────────────────────
FROM python:3.12-slim AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH=/home/nasoma/.local/bin:$PATH \
    PORT=8000

# Dépendances runtime minimales
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    libjpeg62-turbo \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --shell /bin/bash --uid 1000 nasoma

WORKDIR /app

# Copier les dépendances Python depuis le builder
COPY --from=builder --chown=nasoma:nasoma /root/.local /home/nasoma/.local

# Copier le code applicatif
COPY --chown=nasoma:nasoma app/ ./app/
COPY --chown=nasoma:nasoma alembic/ ./alembic/
COPY --chown=nasoma:nasoma alembic.ini ./

USER nasoma

# Healthcheck pour Cloud Run
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

EXPOSE 8000

# Cloud Run injecte $PORT — uvicorn doit y écouter
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1"]
