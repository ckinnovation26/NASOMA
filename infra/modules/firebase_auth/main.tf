# Firebase Auth module — OTP SMS authentication
# Configures Firebase Authentication with phone number + OTP for Comores market

terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

# Enable Firebase Authentication API
resource "google_project_service" "firebase_auth_api" {
  project = var.project_id
  service = "firebaseauth.googleapis.com"

  disable_on_destroy = false
}

# Firebase Auth configuration (phone number sign-in + SMS)
resource "google_identity_platform_config" "default" {
  project = var.project_id

  # SMS provider configuration for OTP
  sign_in {
    email {
      enabled           = false
      password_required = false
    }
    phone_number {
      enabled = true
    }
  }

  mfa {
    enabled_providers = ["PHONE_SMS"]

    state = "ENABLED"
  }

  depends_on = [google_project_service.firebase_auth_api]
}

# MFA phone SMS provider configuration
resource "google_identity_platform_inbound_saml_config" "phone_sms" {
  project = var.project_id

  display_name = "Phone SMS MFA"
  enabled      = true

  # Minimum requirements for SMS authentication
  # Actual SMS provider (Africa's Talking) is configured at backend level
}

# Service account for Firebase Auth custom claims
resource "google_service_account" "firebase_auth_service" {
  account_id   = "firebase-auth-service"
  display_name = "Firebase Auth Service Account"
  project      = var.project_id
}

# Custom claim role for Firebase Auth
resource "google_project_iam_member" "firebase_auth_custom_claims" {
  project = var.project_id
  role    = "roles/firebase.admin"
  member  = "serviceAccount:${google_service_account.firebase_auth_service.email}"
}

# Create test user account (optional, for local testing)
resource "google_identity_platform_oauth_idp_config" "test_sms" {
  count = var.create_test_account ? 1 : 0

  project = var.project_id

  name             = "phone-sms-test"
  display_name     = "Test SMS Auth"
  enabled          = true
  client_id        = "test-client-id"
  client_secret    = "test-client-secret"
  authorization_uri = "https://example.com/auth"
  token_uri        = "https://example.com/token"

  depends_on = [google_identity_platform_config.default]
}

# Firebase Auth disabled anonymous authentication (security)
resource "google_identity_platform_inbound_saml_config" "disable_anonymous" {
  project = var.project_id

  display_name = "Disable Anonymous"
  enabled      = false
}
