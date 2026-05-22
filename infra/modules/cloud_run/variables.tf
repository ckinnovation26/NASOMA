variable "project_id" { type = string }
variable "region" { type = string }
variable "service_name" { type = string }
variable "image" { type = string }
variable "min_instances" { type = number; default = 0 }
variable "max_instances" { type = number; default = 5 }
variable "cpu" { type = string; default = "1" }
variable "memory" { type = string; default = "512Mi" }
variable "env_vars" { type = map(string); default = {} }
