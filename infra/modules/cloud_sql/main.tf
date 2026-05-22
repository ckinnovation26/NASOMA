resource "google_sql_database_instance" "main" {
  project          = var.project_id
  name             = var.instance_name
  region           = var.region
  database_version = var.database_version

  deletion_protection = var.deletion_protection

  settings {
    tier = var.tier

    availability_type = var.high_availability ? "REGIONAL" : "ZONAL"
    disk_type         = "PD_SSD"
    disk_size         = var.disk_size_gb

    backup_configuration {
      enabled                        = var.backup_enabled
      point_in_time_recovery_enabled = var.backup_enabled
      start_time                     = "02:00"
      backup_retention_settings {
        retained_backups = 7
      }
    }

    ip_configuration {
      ipv4_enabled = true
      require_ssl  = true
    }

    insights_config {
      query_insights_enabled = true
    }

    user_labels = {
      env     = var.env
      project = "nasoma"
    }
  }
}

resource "google_sql_database" "nasoma" {
  project  = var.project_id
  instance = google_sql_database_instance.main.name
  name     = "nasoma"
}

resource "random_password" "db_password" {
  length  = 32
  special = true
}

resource "google_sql_user" "app_user" {
  project  = var.project_id
  instance = google_sql_database_instance.main.name
  name     = "nasoma_app"
  password = random_password.db_password.result
}

resource "google_secret_manager_secret" "db_password" {
  project   = var.project_id
  secret_id = "${var.instance_name}-db-password"

  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "db_password" {
  secret      = google_secret_manager_secret.db_password.id
  secret_data = random_password.db_password.result
}
