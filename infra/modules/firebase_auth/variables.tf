variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "region" {
  description = "GCP region for Firebase Auth"
  type        = string
  default     = "africa-south1"
}

variable "create_test_account" {
  description = "Whether to create test SMS authentication account (local testing only)"
  type        = bool
  default     = false
}
