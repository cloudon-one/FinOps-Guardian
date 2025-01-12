
# Recommander SA
resource "google_service_account" "recommender_service_account" {
  project      = var.gcp_project
  account_id   = "organization-checker"
  display_name = "SA For Organization Recommender"
  depends_on = [
    google_project_service.recommender_service
  ]
}

locals {
  permissions = toset([
    "roles/cloudasset.viewer",
    "roles/recommender.computeViewer",
    "roles/recommender.cloudsqlViewer",
    "roles/recommender.iamViewer",
    "roles/storage.objectCreator",
    "roles/recommender.cloudAssetInsightsViewer",
    "roles/recommender.billingAccountCudViewer",
    "roles/recommender.ucsViewer",
    "roles/recommender.projectCudViewer",
    "roles/recommender.productSuggestionViewer",
    "roles/recommender.firewallViewer",
    "roles/recommender.errorReportingViewer",
    "roles/recommender.dataflowDiagnosticsViewer",
    "roles/recommender.containerDiagnosisViewer"
  ])
}

# IAM
resource "google_organization_iam_member" "recommender_iam_members" {
  for_each = local.permissions
  org_id   = var.organization_id
  role     = each.value
  member   = "serviceAccount:${google_service_account.recommender_service_account.email}"
}

resource "google_pubsub_topic" "recommender_checker_topic" {
  project = var.gcp_project
  name    = "organization-checker"
  depends_on = [
    google_project_service.recommender_service
  ]
}

data "archive_file" "recommender_checker_archive" {
  type        = "zip"
  source_dir  = "${path.module}/scripts/cloudfunctions/recommender-checker"
  output_path = "${path.module}/scripts/cloudfunctions/recommender-checker.zip"
}

# GCS bucket

resource "google_storage_bucket" "org_recommender" {
  name                        = var.recommender_bucket
  location                    = "EU"
  project                     = var.gcp_project
  uniform_bucket_level_access = true
  force_destroy               = true
}
resource "google_storage_bucket_object" "recommender_checker_object" {
  name   = "terraform/cloudfunctions/recommender-checker-${data.archive_file.recommender_checker_archive.output_md5}.zip"
  bucket = google_storage_bucket.org_recommender.name
  source = data.archive_file.recommender_checker_archive.output_path
}

# Cloud Function
resource "google_cloudfunctions_function" "recommender_checker_func" {
  project     = var.gcp_project
  region      = var.gcp_region
  name        = "org-checker"
  description = "check recommendation within GCP Org"
  runtime     = "python39"

  available_memory_mb   = 512
  source_archive_bucket = google_storage_bucket.org_recommender.name
  source_archive_object = google_storage_bucket_object.recommender_checker_object.name
  timeout               = 300
  entry_point           = "check_recommender"

  event_trigger {
    event_type = "google.pubsub.topic.publish"
    resource   = google_pubsub_topic.recommender_checker_topic.name
    failure_policy {
      retry = false
    }
  }

  environment_variables = {
    ORGANIZATION_ID                    = var.organization_id
    SLACK_HOOK_URL                     = var.slack_webhook_url
    IDLE_VM_RECOMMENDER_ENABLED        = var.idle_vm_recommender_enabled
    IDLE_SQL_RECOMMENDER_ENABLED       = var.idle_sql_recommender_enabled
    IDLE_DISK_RECOMMENDER_ENABLED      = var.idle_disk_recommender_enabled
    IDLE_IMAGE_RECOMMENDER_ENABLED     = var.idle_image_recommender_enabled
    IDLE_IP_RECOMMENDER_ENABLED        = var.idle_ip_recommender_enabled
    RIGHTSIZE_VM_RECOMMENDER_ENABLED   = var.rightsize_vm_recommender_enabled
    RIGHTSIZE_SQL_RECOMMENDER_ENABLED  = var.rightsize_sql_recommender_enabled
    COMMITMENT_USE_RECOMMENDER_ENABLED = var.commitment_use_recommender_enabled
    BILLING_USE_RECOMMENDER_ENABLED    = var.billing_use_recommender_enabled
  }
  service_account_email = google_service_account.recommender_service_account.email
}

# Scheduler
resource "google_cloud_scheduler_job" "recommender_checker_scheduler" {
  project     = var.gcp_project
  region      = var.gcp_region
  name        = "org_checker_scheduler"
  description = "check Recommender for all GCP projects"
  schedule    = var.job_schedule
  time_zone   = var.job_timezone

  pubsub_target {
    topic_name = google_pubsub_topic.recommender_checker_topic.id
    data       = base64encode("{}")
  }
  retry_config {
    max_backoff_duration = "3600s"
    max_doublings        = 5
    max_retry_duration   = "30s"
    min_backoff_duration = "5s"
    retry_count          = 3
  }
}
