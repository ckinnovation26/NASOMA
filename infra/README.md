# Nasoma — Infrastructure (Terraform GCP)

Infrastructure-as-Code pour déployer Nasoma sur **Google Cloud `africa-south1`** (Johannesburg).

## Prérequis

- Terraform ≥ 1.9
- gcloud CLI authentifié (`gcloud auth application-default login`)
- Projet GCP créé + facturation activée
- APIs activées : Cloud Run, Cloud SQL, Firestore, Cloud Storage, Secret Manager, Vision API, Cloud Tasks

```bash
gcloud services enable \
  run.googleapis.com \
  sqladmin.googleapis.com \
  firestore.googleapis.com \
  storage.googleapis.com \
  secretmanager.googleapis.com \
  vision.googleapis.com \
  cloudtasks.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  cloudbilling.googleapis.com
```

## Structure

```
infra/
├── modules/
│   ├── cloud_run/        Service FastAPI auto-scale
│   ├── cloud_sql/        Postgres 16 (db-f1-micro en dev, db-custom en prod)
│   ├── firestore/        Native mode, africa-south1
│   ├── storage/          Bucket scans (TTL 30j)
│   └── budget/           Kill-switch budget par tenant
├── environments/
│   ├── dev/              Configuration dev (free tier max)
│   └── prod/             Configuration prod
└── README.md
```

## Déployer dev

```bash
cd infra/environments/dev
terraform init
terraform plan -var-file=terraform.tfvars
terraform apply -var-file=terraform.tfvars
```

## Coûts cibles

| Env | Compute | DB | Storage | Total/mois |
|---|---|---|---|---|
| dev | Cloud Run min=0 | db-f1-micro | 5 GB | ~10 $ |
| prod (Y1) | Cloud Run min=1 | db-custom-1-3840 | 50 GB | ~75 $ |
| prod (Y2 — 50k users) | Cloud Run min=2 | db-custom-2-7680 | 500 GB | ~250 $ |

→ Voir `docs/runbook.md` pour la procédure complète de déploiement.

## Kill-switch budget

Chaque environnement a un `module "budget"` qui crée :
- Une alerte Cloud Billing à 50 %, 80 %, 100 % du budget mensuel
- Une Cloud Function `daily-budget-check` qui désactive Vision API + Gemini si seuil dépassé
- Notification email + Slack

→ Critique pour la viabilité économique (cf. `docs/pricing.md`).
