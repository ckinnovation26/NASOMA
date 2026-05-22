variable "project_id" { type = string }
variable "region" { type = string }
variable "name" { type = string }
variable "ttl_days" { type = number; default = 30 }
variable "env" { type = string; default = "dev" }
