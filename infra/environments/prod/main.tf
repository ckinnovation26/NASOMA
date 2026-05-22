terraform {
  required_version = ">= 1.9"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 6.10"
    }
  }

  backend "gcs" {
    bucket = "nasoma-tfstate-prod"
    prefix = "prod"
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# Storage prod — bucket multi-régional pour résilience
module "scans_bucket" {
  source = "../../modules/storage"

  project_id = var.project_id
  region     = var.region
  name       = "${var.project_id}-scans"
  ttl_days   = 30
  env        = "prod"
}

# Firestore prod
module "firestore" {
  source = "../../modules/firestore"

  project_id = var.project_id
  location   = var.firestore_location
}

# Postgres prod — instance dédiée + HA
module "postgres" {
  source = "../../modules/cloud_sql"

  project_id          = var.project_id
  region              = var.region
  instance_name       = "nasoma-pg-prod"
  database_version    = "POSTGRES_16"
  tier                = "db-custom-1-3840"
  disk_size_gb        = 50
  deletion_protection = true
  high_availability   = true
  backup_enabled      = true
  env                 = "prod"
}

# Backend prod — min_instances=1 pour éviter cold starts
module "backend" {
  source = "../../modules/cloud_run"

  project_id    = var.project_id
  region        = var.region
  service_name  = "nasoma-backend-prod"
  image         = var.backend_image
  min_instances = 1
  max_instances = 10
  cpu           = "1"
  memory        = "1Gi"
  env_vars = {
    APP_ENV              = "prod"
    DATABASE_URL         = module.postgres.connection_string
    FIRESTORE_PROJECT_ID = var.project_id
    GCP_STORAGE_BUCKET   = module.scans_bucket.bucket_name
  }
}

# Budget kill-switch prod
module "budget" {
  source = "../../modules/budget"

  project_id          = var.project_id
  billing_account     = var.billing_account
  monthly_budget_usd  = 200                       # ajusté selon trafic
  notification_emails = var.alert_emails
}
