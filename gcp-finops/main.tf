
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

# IAM - Organization level (only if scan_scope is organization)
resource "google_organization_iam_member" "recommender_iam_members" {
  for_each = var.scan_scope == "organization" ? local.permissions : []
  org_id   = var.organization_id
  role     = each.value
  member   = "serviceAccount:${google_service_account.recommender_service_account.email}"
}

# IAM - Project level (only if scan_scope is project)
resource "google_project_iam_member" "recommender_project_iam_members" {
  for_each = var.scan_scope == "project" ? local.permissions : []
  project  = var.gcp_project
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
# Secret Manager for Slack webhook (optional)
resource "google_secret_manager_secret" "slack_webhook" {
  count     = var.use_secret_manager ? 1 : 0
  project   = var.gcp_project
  secret_id = "slack-webhook-url"

  replication {
    auto {}
  }

  depends_on = [google_project_service.recommender_service]
}

resource "google_secret_manager_secret_version" "slack_webhook_version" {
  count       = var.use_secret_manager ? 1 : 0
  secret      = google_secret_manager_secret.slack_webhook[0].id
  secret_data = var.slack_webhook_url
}

# IAM for Cloud Function to access secret
resource "google_secret_manager_secret_iam_member" "function_secret_accessor" {
  count     = var.use_secret_manager ? 1 : 0
  project   = var.gcp_project
  secret_id = google_secret_manager_secret.slack_webhook[0].secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.recommender_service_account.email}"
}

# Cloud Function
resource "google_cloudfunctions_function" "recommender_checker_func" {
  project     = var.gcp_project
  region      = var.gcp_region
  name        = "org-checker"
  description = "check recommendation within GCP Org"
  runtime     = "python312"

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

  environment_variables = merge(
    {
      GCP_PROJECT                        = var.gcp_project
      SCAN_SCOPE                         = var.scan_scope
      ORGANIZATION_ID                    = var.organization_id
      MIN_COST_THRESHOLD                 = var.min_cost_threshold
      USE_SECRET_MANAGER                 = var.use_secret_manager
      IDLE_VM_RECOMMENDER_ENABLED        = var.idle_vm_recommender_enabled
      IDLE_SQL_RECOMMENDER_ENABLED       = var.idle_sql_recommender_enabled
      IDLE_DISK_RECOMMENDER_ENABLED      = var.idle_disk_recommender_enabled
      IDLE_IMAGE_RECOMMENDER_ENABLED     = var.idle_image_recommender_enabled
      IDLE_IP_RECOMMENDER_ENABLED        = var.idle_ip_recommender_enabled
      RIGHTSIZE_VM_RECOMMENDER_ENABLED   = var.rightsize_vm_recommender_enabled
      RIGHTSIZE_SQL_RECOMMENDER_ENABLED  = var.rightsize_sql_recommender_enabled
      MIG_RIGHTSIZE_RECOMMENDER_ENABLED  = var.mig_rightsize_recommender_enabled
      COMMITMENT_USE_RECOMMENDER_ENABLED = var.commitment_use_recommender_enabled
      BILLING_USE_RECOMMENDER_ENABLED    = var.billing_use_recommender_enabled
    },
    var.use_secret_manager ? {
      SLACK_WEBHOOK_SECRET_NAME = google_secret_manager_secret_version.slack_webhook_version[0].name
    } : {
      SLACK_HOOK_URL = var.slack_webhook_url
    }
  )
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
