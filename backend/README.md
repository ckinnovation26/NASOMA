# Nasoma — Backend FastAPI

Backend Python 3.12 déployé sur **Google Cloud Run** (région `africa-south1`).

## Démarrage local

```bash
# 1. Lancer Postgres + Firestore emulator
cd ..  # racine du repo
docker-compose up -d

# 2. Installer les dépendances
cd backend
python -m venv .venv
source .venv/bin/activate           # Linux/macOS
# .venv\Scripts\activate            # Windows PowerShell
pip install -e ".[dev]"

# 3. Configurer
cp ../.env.example ../.env          # éditer .env avec vos clés API

# 4. Migrations
alembic upgrade head

# 5. Lancer le serveur
uvicorn app.main:app --reload --port 8000
```

→ API : http://localhost:8000
→ Docs OpenAPI : http://localhost:8000/docs
→ Healthcheck : http://localhost:8000/health

## Structure

```
backend/
├── app/
│   ├── api/v1/         Endpoints REST (auth, scans, quota, sessions, payments)
│   ├── core/           Config, logging, security (JWT, HMAC)
│   ├── db/             Sessions Postgres + Firestore
│   ├── models/         Modèles SQLAlchemy
│   ├── schemas/        Pydantic v2 (contrats API)
│   ├── services/       OCR, BKT, quota, payment, notifications
│   ├── workers/        Cloud Tasks handlers
│   └── main.py         Point d'entrée FastAPI
├── alembic/            Migrations DB
├── scripts/            init_db.sql, batch jobs
├── tests/              Pytest (couverture ≥ 80 %)
├── Dockerfile          Image Cloud Run (multi-stage)
└── pyproject.toml
```

## Tests

```bash
pytest                                          # tous les tests
pytest --cov=app --cov-report=html              # avec couverture
pytest -m "not slow"                            # exclure les tests lents
pytest -m integration                           # uniquement intégration
```

## Qualité de code

```bash
ruff check .          # linter
ruff format .         # formatter
mypy app              # type-checking
```

## Migrations Alembic

```bash
# Créer une migration auto à partir des modèles
alembic revision --autogenerate -m "add users table"

# Appliquer
alembic upgrade head

# Annuler
alembic downgrade -1
```

## Variables d'environnement

Voir `../.env.example`. Variables critiques :

| Variable | Description |
|---|---|
| `DATABASE_URL` | URL Postgres async (`postgresql+asyncpg://...`) |
| `FIRESTORE_PROJECT_ID` | Projet GCP Firestore |
| `GEMINI_API_KEY` | Clé Gemini API |
| `JWT_SECRET` | Secret JWT (32 chars hex min) |
| `QUOTA_FREE_LIFETIME_SCANS` | **3** (verrouillé business) |

## Déploiement

Voir [`../docs/runbook.md`](../docs/runbook.md).
