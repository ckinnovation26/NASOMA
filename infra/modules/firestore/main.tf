resource "google_firestore_database" "main" {
  project     = var.project_id
  name        = "(default)"
  location_id = var.location
  type        = "FIRESTORE_NATIVE"

  concurrency_mode            = "OPTIMISTIC"
  app_engine_integration_mode = "DISABLED"

  delete_protection_state = "DELETE_PROTECTION_ENABLED"
}

# Index composé pour les requêtes quota (user + plan + expires_at)
resource "google_firestore_index" "quota_lookup" {
  project    = var.project_id
  database   = google_firestore_database.main.name
  collection = "user_quotas"

  fields {
    field_path = "user_id"
    order      = "ASCENDING"
  }

  fields {
    field_path = "expires_at"
    order      = "ASCENDING"
  }
}
