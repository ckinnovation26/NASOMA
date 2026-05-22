variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "region" {
  description = "GCP region for Cloud Tasks queue"
  type        = string
  default     = "africa-south1"
}

variable "max_concurrent_dispatches" {
  description = "Max number of concurrent task dispatches"
  type        = number
  default     = 100
}

variable "max_dispatches_per_second" {
  description = "Max number of task dispatches per second"
  type        = number
  default     = 10
}

variable "max_retry_attempts" {
  description = "Max number of retry attempts for failed tasks"
  type        = number
  default     = 5
}

variable "max_retry_duration" {
  description = "Max duration for retrying failed tasks (seconds)"
  type        = string
  default     = "604800s"
}

variable "backend_host" {
  description = "Backend Cloud Run service host"
  type        = string
}

variable "backend_service_name" {
  description = "Backend Cloud Run service name"
  type        = string
}

variable "service_account_email" {
  description = "Service account email for task authentication"
  type        = string
}

variable "create_iam_binding" {
  description = "Whether to create IAM binding for task invoker"
  type        = bool
  default     = true
}
