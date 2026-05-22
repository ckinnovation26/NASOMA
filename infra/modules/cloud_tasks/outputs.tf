output "queue_name" {
  description = "Full name of the Cloud Tasks queue"
  value       = google_cloud_tasks_queue.ocr_worker_queue.name
}

output "queue_path" {
  description = "Full path of the Cloud Tasks queue"
  value       = google_cloud_tasks_queue.ocr_worker_queue.id
}

output "service_account_email" {
  description = "Email of the Cloud Tasks invoker service account"
  value       = google_service_account.cloud_tasks_invoker.email
}

output "service_account_id" {
  description = "ID of the Cloud Tasks invoker service account"
  value       = google_service_account.cloud_tasks_invoker.id
}
