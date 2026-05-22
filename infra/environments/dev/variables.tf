variable "project_id" {
  type        = string
  description = "ID du projet GCP (ex: nasoma-dev-426510)"
}

variable "region" {
  type        = string
  default     = "africa-south1"
  description = "Région GCP — Johannesburg"
}

variable "firestore_location" {
  type        = string
  default     = "africa-south1"
  description = "Région Firestore"
}

variable "backend_image" {
  type        = string
  description = "Image Docker du backend (ex: africa-south1-docker.pkg.dev/PROJET/nasoma/backend:latest)"
}

variable "billing_account" {
  type        = string
  description = "ID du compte de facturation (ex: 012345-678901-ABCDEF)"
}

variable "alert_emails" {
  type        = list(string)
  default     = ["kader@ckinnovation.fr"]
  description = "Adresses pour les alertes budget"
}
