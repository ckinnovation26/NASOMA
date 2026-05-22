# Nasoma — *Mimi, Nasoma. — Moi, j'étudie.*

> Application Android EdTech qui aide les élèves africains à corriger leurs lacunes scolaires quotidiennes grâce à l'IA Vision.

[![Stack](https://img.shields.io/badge/stack-Africa--first-success)](docs/architecture.md)
[![Cloud](https://img.shields.io/badge/cloud-GCP%20africa--south1-blue)](docs/runbook.md)
[![Status](https://img.shields.io/badge/status-MVP%20Sprint%201-orange)](docs/architecture.md)

---

## 🎯 Mission

MVP pour pilote 200-500 élèves en Union des Comores (CM1-CM2-6ᵉ). Workflow : élève prend en photo sa copie corrigée → IA analyse les erreurs → 3-4 micro-exercices ciblés.

## 🧱 Stack

| Composant | Choix |
|---|---|
| Mobile | Flutter 3.22 + Riverpod + go_router |
| Backend | Python FastAPI sur Cloud Run |
| Cloud | GCP `africa-south1` (Johannesburg) |
| DB | Firestore (temps réel) + Cloud SQL Postgres (BI/BKT) |
| OCR | ML Kit local → Cloud Vision → Gemini 2.0 Flash |
| LLM | Gemini 1.5 Flash-8B |
| Auth | Firebase Phone OTP |
| Push / SMS | FCM + Africa's Talking |
| Paiement | Hollo Money + tickets physiques |

→ Voir `docs/architecture.md` pour le détail.

## 📁 Structure

```
.
├── backend/        FastAPI Python 3.12 (Cloud Run)
├── mobile/         Flutter app
├── pedagogy/       Knowledge graphs JSON + exercises seed (650 concepts APC_KM)
├── infra/          Terraform GCP
├── docs/           Architecture, API, runbook, pricing, security
├── docker-compose.yml
├── .env.example
└── README.md
```

## 🚀 Démarrage rapide

### Prérequis
- Docker + Docker Compose
- Python 3.12+
- Flutter 3.22+
- Node.js 20+ (pour Firebase emulator)
- gcloud CLI (déploiement prod)

### Lancer le backend en local

```bash
cp .env.example .env
docker-compose up -d                  # Postgres + Firestore emulator
cd backend
python -m venv .venv && source .venv/bin/activate   # ou .venv\Scripts\activate sur Windows
pip install -e ".[dev]"
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

→ API disponible sur `http://localhost:8000` — Healthcheck : `http://localhost:8000/health`
→ Docs OpenAPI : `http://localhost:8000/docs`

### Lancer l'app mobile

```bash
cd mobile
flutter create .                      # première fois uniquement (génère android/ ios/)
flutter pub get
flutter run                           # device ou émulateur Android
```

### Tests

```bash
# Backend
cd backend && pytest --cov=app --cov-report=term-missing

# Mobile
cd mobile && flutter test
```

## 💰 Modèle économique — **AUCUN scan gratuit illimité, jamais**

| Plan | Prix | Quota |
|---|---|---|
| Découverte | Gratuit | **3 scans valables 7 jours** (puis grace + gel comme paid) |
| Ticket Journalier | 100 KMF (~0,20 €) | 5 scans / 24h |
| **Ticket 3 Jours** | **250 KMF (~0,50 €)** | **15 scans / 3 jours** |
| Hebdo | 500 KMF (~1 €) | 30 scans / semaine |
| **Mensuel (par enfant)** | **1 500 KMF / enfant / mois** | **120 scans / mois / enfant** |
| École B2B | Négocié | Quota par classe |

> Famille : facturation linéaire par enfant (1 enfant = 1 500, 3 enfants = 4 500 KMF/mois). Jusqu'à 4 profils.

→ Voir `docs/pricing.md`.

## 📚 Documentation

- [`docs/strategie_Nasoma.md`](docs/strategie_Nasoma.md) — **Stratégie & moats défensifs (à lire en premier)**
- [`docs/architecture.md`](docs/architecture.md) — Vue d'ensemble technique
- [`docs/api.md`](docs/api.md) — Référence API REST
- [`docs/runbook.md`](docs/runbook.md) — Déploiement & exploitation
- [`docs/pricing.md`](docs/pricing.md) — Modèle tarifaire & anti-abus
- [`docs/security.md`](docs/security.md) — Sécurité, conformité, RGPD/COPPA

## 🤝 Contribution

- Branches : `main` (prod), `develop` (intégration), `feat/xxx`, `fix/xxx`
- Commits : [Conventional Commits](https://www.conventionalcommits.org/)
- Avant chaque commit : `pytest && flutter test && flutter analyze`

## 📜 Licence

Propriétaire — CK Innovation SARL © 2026. Tous droits réservés.

---

*Pour les contributeurs IA : lire `NASOMA_PROMPT_POUR_IA_CODEUSE.md` AVANT toute action.*
