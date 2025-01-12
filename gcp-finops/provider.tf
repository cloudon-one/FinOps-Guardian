provider "google" {
  credentials = file("creds/serviceaccount.json")
  project     = var.gcp_project
  region      = var.gcp_region
}
