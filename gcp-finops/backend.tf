terraform {
  backend "gcs" {
    bucket = "finops-state-bucket"
    prefix = "recommender/org-checker"
  }
}
