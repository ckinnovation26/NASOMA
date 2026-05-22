# Cloud Tasks module — OCR worker queue
# Dispatches scan processing jobs to backend workers

resource "google_cloud_tasks_queue" "ocr_worker_queue" {
  name     = "ocr-worker-queue"
  location = var.region
  project  = var.project_id

  rate_limits {
    max_concurrent_dispatches = var.max_concurrent_dispatches
    max_dispatches_per_second = var.max_dispatches_per_second
  }

  retry_config {
    max_attempts       = var.max_retry_attempts
    max_retry_duration = var.max_retry_duration
  }

  http_target {
    http_method = "POST"
    uri_override {
      scheme = "https"
      host   = var.backend_host
      path   = "/workers/ocr"
    }
    oidc_token {
      service_account_email = var.service_account_email
    }
  }

  depends_on = [google_project_service.cloud_tasks_api]
}

# Enable Cloud Tasks API if not already enabled
resource "google_project_service" "cloud_tasks_api" {
  project = var.project_id
  service = "cloudtasks.googleapis.com"

  disable_on_destroy = false
}

# Service account for Cloud Tasks to call backend
resource "google_service_account" "cloud_tasks_invoker" {
  account_id   = "cloud-tasks-invoker"
  display_name = "Cloud Tasks Invoker (OCR Worker)"
  project      = var.project_id
}

# Grant Cloud Tasks permission to invoke backend
resource "google_cloud_run_service_iam_member" "cloud_tasks_invoker" {
  count = var.create_iam_binding ? 1 : 0

  service  = var.backend_service_name
  location = var.region
  role     = "roles/run.invoker"
  member   = "serviceAccount:${google_service_account.cloud_tasks_invoker.email}"
  project  = var.project_id
}
