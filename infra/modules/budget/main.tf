resource "google_billing_budget" "main" {
  billing_account = var.billing_account
  display_name    = "Nasoma — Budget mensuel (${var.project_id})"

  budget_filter {
    projects = ["projects/${var.project_id}"]
  }

  amount {
    specified_amount {
      currency_code = "USD"
      units         = var.monthly_budget_usd
    }
  }

  # Alertes à 50%, 80%, 100%
  threshold_rules {
    threshold_percent = 0.5
  }
  threshold_rules {
    threshold_percent = 0.8
  }
  threshold_rules {
    threshold_percent = 1.0
  }

  all_updates_rule {
    monitoring_notification_channels = [
      for ch in google_monitoring_notification_channel.email : ch.id
    ]
    disable_default_iam_recipients = false
  }
}

resource "google_monitoring_notification_channel" "email" {
  for_each     = toset(var.notification_emails)
  project      = var.project_id
  display_name = "Email ${each.value}"
  type         = "email"

  labels = {
    email_address = each.value
  }
}
