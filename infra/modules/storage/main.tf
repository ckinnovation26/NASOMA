resource "google_storage_bucket" "main" {
  project  = var.project_id
  name     = var.name
  location = var.region

  uniform_bucket_level_access = true
  public_access_prevention    = "enforced"

  versioning {
    enabled = false
  }

  # Lifecycle — supprimer les scans après TTL pour économiser
  lifecycle_rule {
    condition {
      age = var.ttl_days
    }
    action {
      type = "Delete"
    }
  }

  # CORS pour upload direct depuis l'app mobile
  cors {
    origin          = ["*"]
    method          = ["GET", "PUT", "POST"]
    response_header = ["Content-Type", "Content-Length"]
    max_age_seconds = 3600
  }

  labels = {
    env     = var.env
    project = "nasoma"
  }
}
