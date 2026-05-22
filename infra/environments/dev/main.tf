terraform {
  required_version = ">= 1.9"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 6.10"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = "~> 6.10"
    }
  }

  backend "gcs" {
    bucket = "nasoma-tfstate-dev"
    prefix = "dev"
    # Créer le bucket avant le premier init :
    # gcloud storage buckets create gs://nasoma-tfstate-dev --location=africa-south1
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

provider "google-beta" {
  project = var.project_id
  region  = var.region
}

# ──────────────────────────────────────────────
#  Storage — bucket pour les images scannées
# ──────────────────────────────────────────────
module "scans_bucket" {
  source = "../../modules/storage"

  project_id = var.project_id
  region     = var.region
  name       = "${var.project_id}-scans"
  ttl_days   = 30
  env        = "dev"
}

# ──────────────────────────────────────────────
#  Firestore — Native mode
# ──────────────────────────────────────────────
module "firestore" {
  source = "../../modules/firestore"

  project_id = var.project_id
  location   = var.firestore_location
}

# ──────────────────────────────────────────────
#  Cloud SQL Postgres — taille minimale (dev)
# ──────────────────────────────────────────────
module "postgres" {
  source = "../../modules/cloud_sql"

  project_id        = var.project_id
  region            = var.region
  instance_name     = "nasoma-pg-dev"
  database_version  = "POSTGRES_16"
  tier              = "db-f1-micro"
  disk_size_gb      = 10
  deletion_protection = false
  env               = "dev"
}

# ──────────────────────────────────────────────
#  Cloud Run — backend FastAPI
# ──────────────────────────────────────────────
module "backend" {
  source = "../../modules/cloud_run"

  project_id   = var.project_id
  region       = var.region
  service_name = "nasoma-backend-dev"
  image        = var.backend_image
  min_instances = 0           # scale-to-zero en dev
  max_instances = 2
  cpu          = "1"
  memory       = "512Mi"
  env_vars = {
    APP_ENV            = "dev"
    DATABASE_URL       = module.postgres.connection_string
    FIRESTORE_PROJECT_ID = var.project_id
    GCP_STORAGE_BUCKET = module.scans_bucket.bucket_name
  }
}

# ──────────────────────────────────────────────
#  Budget kill-switch
# ──────────────────────────────────────────────
module "budget" {
  source = "../../modules/budget"

  project_id     = var.project_id
  billing_account = var.billing_account
  monthly_budget_usd = 50              # alerte si > 50$ en dev
  notification_emails = var.alert_emails
}
