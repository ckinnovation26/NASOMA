output "instance_name" {
  value = google_sql_database_instance.main.name
}

output "connection_name" {
  value = google_sql_database_instance.main.connection_name
}

output "connection_string" {
  sensitive = true
  value     = "postgresql+asyncpg://${google_sql_user.app_user.name}:${random_password.db_password.result}@${google_sql_database_instance.main.public_ip_address}:5432/${google_sql_database.nasoma.name}"
}

output "password_secret_id" {
  value = google_secret_manager_secret.db_password.secret_id
}
