# Nasoma — Runbook ops

## Déploiement initial

### 1. Créer le projet GCP

```bash
# Créer projet
gcloud projects create nasoma-prod-XXXXX --name="Nasoma Production"

# Lier compte de facturation
gcloud beta billing projects link nasoma-prod-XXXXX \
  --billing-account=012345-678901-ABCDEF

# Sélectionner
gcloud config set project nasoma-prod-XXXXX
```

### 2. Activer les APIs

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
  cloudbilling.googleapis.com \
  generativelanguage.googleapis.com
```

### 3. Créer le bucket d'état Terraform

```bash
gsutil mb -p nasoma-prod-XXXXX -l africa-south1 gs://nasoma-tfstate-prod
gsutil versioning set on gs://nasoma-tfstate-prod
```

### 4. Créer Artifact Registry pour les images Docker

```bash
gcloud artifacts repositories create nasoma \
  --repository-format=docker \
  --location=africa-south1 \
  --description="Nasoma Docker images"
```

### 5. Premier deploy infra

```bash
cd infra/environments/prod
cp terraform.tfvars.example terraform.tfvars   # éditer avec les vraies valeurs
terraform init
terraform plan
terraform apply
```

### 6. Build & push image backend

```bash
cd backend
gcloud auth configure-docker africa-south1-docker.pkg.dev

docker build -t africa-south1-docker.pkg.dev/nasoma-prod-XXXXX/nasoma/backend:v0.1.0 .
docker push africa-south1-docker.pkg.dev/nasoma-prod-XXXXX/nasoma/backend:v0.1.0
```

### 7. Déployer Cloud Run

```bash
# Via Terraform (recommandé)
cd infra/environments/prod
terraform apply -var="backend_image=africa-south1-docker.pkg.dev/nasoma-prod-XXXXX/nasoma/backend:v0.1.0"

# Ou via gcloud
gcloud run deploy nasoma-backend-prod \
  --image=africa-south1-docker.pkg.dev/nasoma-prod-XXXXX/nasoma/backend:v0.1.0 \
  --region=africa-south1 \
  --platform=managed
```

## Procédures courantes

### Rollback Cloud Run

```bash
# Lister les révisions
gcloud run revisions list --service=nasoma-backend-prod --region=africa-south1

# Router 100% du trafic vers une révision précédente
gcloud run services update-traffic nasoma-backend-prod \
  --to-revisions=nasoma-backend-prod-00012-abc=100 \
  --region=africa-south1
```

### Appliquer une migration Alembic en prod

```bash
# Récupérer la connection string depuis Secret Manager
DB_URL=$(gcloud secrets versions access latest --secret=nasoma-pg-prod-db-password)

# Lancer via Cloud Run Jobs (recommandé)
gcloud run jobs create migrate-job \
  --image=africa-south1-docker.pkg.dev/nasoma-prod-XXXXX/nasoma/backend:v0.1.0 \
  --command="alembic" --args="upgrade,head" \
  --region=africa-south1 \
  --set-env-vars="DATABASE_URL=$DB_URL"

gcloud run jobs execute migrate-job --region=africa-south1
```

### Voir les logs

```bash
# Stream en temps réel
gcloud run services logs tail nasoma-backend-prod --region=africa-south1

# Filtrer par sévérité
gcloud logging read 'resource.type=cloud_run_revision AND severity>=ERROR' --limit=50
```

### Restaurer Cloud SQL depuis un backup

```bash
gcloud sql backups list --instance=nasoma-pg-prod
gcloud sql backups restore BACKUP_ID --restore-instance=nasoma-pg-prod
```

### Activer le kill-switch budget manuellement

```bash
# Désactiver Vision API
gcloud services disable vision.googleapis.com

# Désactiver Gemini
gcloud services disable generativelanguage.googleapis.com

# Réactiver après résolution
gcloud services enable vision.googleapis.com generativelanguage.googleapis.com
```

## Monitoring

| Dashboard | URL |
|---|---|
| Cloud Run | `console.cloud.google.com/run` |
| Cloud SQL | `console.cloud.google.com/sql` |
| Firestore usage | `console.cloud.google.com/firestore/data/usage` |
| Vision API quota | `console.cloud.google.com/apis/api/vision.googleapis.com/quotas` |
| Gemini billing | `console.cloud.google.com/billing` |
| Budget alerts | `console.cloud.google.com/billing/01234/budgets` |
| Crashlytics | `console.firebase.google.com/project/nasoma-prod/crashlytics` |

## Alertes critiques

| Alerte | Seuil | Action |
|---|---|---|
| Budget mensuel | 80 % | Vérifier coûts/scan, possibles abus |
| Budget mensuel | 100 % | Kill-switch automatique |
| Erreur 5xx | > 1 %/min | Pager on-call |
| Latence P95 | > 2s | Investiguer DB / OCR |
| Vision API quota | 80 % | Augmenter quota ou throttle |

## Procédure d'incident

1. **Détecter** : alerte Pagerduty / email budget
2. **Communiquer** : message dans #nasoma-incidents Slack
3. **Diagnostiquer** : logs Cloud Logging + traces
4. **Atténuer** : rollback ou kill-switch
5. **Résoudre** : fix + re-deploy
6. **Post-mortem** : 24h après, créer un doc dans `/docs/incidents/`
