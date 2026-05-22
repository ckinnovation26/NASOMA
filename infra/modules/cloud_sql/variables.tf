variable "project_id" { type = string }
variable "region" { type = string }
variable "instance_name" { type = string }
variable "database_version" { type = string; default = "POSTGRES_16" }
variable "tier" { type = string; default = "db-f1-micro" }
variable "disk_size_gb" { type = number; default = 10 }
variable "deletion_protection" { type = bool; default = true }
variable "high_availability" { type = bool; default = false }
variable "backup_enabled" { type = bool; default = false }
variable "env" { type = string; default = "dev" }

terraform {
  required_providers {
    random = { source = "hashicorp/random" }
  }
}
