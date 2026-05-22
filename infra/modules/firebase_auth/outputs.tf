output "service_account_email" {
  description = "Email of the Firebase Auth service account"
  value       = google_service_account.firebase_auth_service.email
}

output "service_account_id" {
  description = "ID of the Firebase Auth service account"
  value       = google_service_account.firebase_auth_service.id
}

output "firebase_auth_api_enabled" {
  description = "Whether Firebase Authentication API is enabled"
  value       = google_project_service.firebase_auth_api.service
}
