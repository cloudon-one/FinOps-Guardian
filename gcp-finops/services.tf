locals {
  services = toset([
    "cloudasset.googleapis.com",
    "cloudbuild.googleapis.com",
    "cloudfunctions.googleapis.com",
    "cloudscheduler.googleapis.com",
    "recommender.googleapis.com",
    "serviceusage.googleapis.com",
    "cloudresourcemanager.googleapis.com",
    "secretmanager.googleapis.com"
  ])
}

resource "google_project_service" "recommender_service" {
  for_each           = local.services
  project            = var.gcp_project
  service            = each.value
  disable_on_destroy = false
}
