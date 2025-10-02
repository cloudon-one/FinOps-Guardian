terraform {
  backend "gcs" {
    bucket = "finsec-cloud-finops-state"
    prefix = "recommender/org-checker"
  }
}
