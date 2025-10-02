provider "google" {
  # Use Application Default Credentials (ADC) or Workload Identity
  # Set GOOGLE_APPLICATION_CREDENTIALS environment variable or use gcloud auth application-default login
  project = var.gcp_project
  region  = var.gcp_region
}
