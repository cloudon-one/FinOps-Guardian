variable "organization_id" {
  type        = string
  description = "REQUIRED: GCP Organization ID"
}

variable "gcp_project" {
  type        = string
  description = "REQUIRED: GCP Project ID to deploy the Cloud Function"
}

variable "gcp_region" {
  type        = string
  default     = "europe-west1"
  description = "OPTIONAL: GCP Region to deploy"
}

variable "recommender_bucket" {
  type        = string
  description = "REQUIRED: GCS bucket to manage Cloud Function codes"
}

variable "slack_webhook_url" {
  type        = string
  description = "REQUIRED: slack webhook URL to notify results"
}

variable "job_schedule" {
  type        = string
  default     = "0 */8 * * *"
  description = "OPTIONAL: a cron expression for periodic execution"
}

variable "job_timezone" {
  type        = string
  default     = "Etc/GMT"
  description = "OPTIONAL: timezone"
}

variable "idle_vm_recommender_enabled" {
  type        = string
  default     = true
  description = "OPTIONAL: Option to enable Idle VM Recommender"
}

variable "idle_disk_recommender_enabled" {
  type        = string
  default     = true
  description = "OPTIONAL: Option to enable Idle Disk Recommender"
}

variable "idle_image_recommender_enabled" {
  type        = string
  default     = true
  description = "OPTIONAL: Option to enable Idle Image Recommender"
}

variable "idle_ip_recommender_enabled" {
  type        = string
  default     = true
  description = "OPTIONAL: Option to enable Idle IP Recommender"
}

variable "idle_sql_recommender_enabled" {
  type        = string
  default     = true
  description = "OPTIONAL: Option to enable Idle SQL Recommender"
}

variable "rightsize_vm_recommender_enabled" {
  type        = string
  default     = true
  description = "OPTIONAL: Option to enable right sized VM Recommender"
}

variable "rightsize_sql_recommender_enabled" {
  type        = string
  default     = true
  description = "OPTIONAL: Option to enable right sized SQL Recommender"
}

variable "commitment_use_recommender_enabled" {
  type        = string
  default     = true
  description = "OPTIONAL: Option to enable Commitment use Recommender"
}

variable "billing_use_recommender_enabled" {
  type        = string
  default     = true
  description = "OPTIONAL: Option to enable Billing use Recommender"
}
