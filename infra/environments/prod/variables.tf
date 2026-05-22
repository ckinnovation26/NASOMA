variable "project_id" {
  type        = string
  description = "ID du projet GCP prod"
}

variable "region" {
  type        = string
  default     = "africa-south1"
}

variable "firestore_location" {
  type        = string
  default     = "africa-south1"
}

variable "backend_image" {
  type        = string
  description = "Image Docker tagguée semver (jamais :latest en prod)"
}

variable "billing_account" {
  type        = string
}

variable "alert_emails" {
  type        = list(string)
  default     = ["kader@ckinnovation.fr"]
}
