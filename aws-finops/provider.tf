terraform {
  required_version = ">= 0.15"
}

provider "aws" {
  region = var.aws_region

  dynamic "assume_role" {
    for_each = var.assume_role_arn != null ? [var.assume_role_arn] : []
    content {
      role_arn = assume_role.value
    }
  }

  default_tags {
    tags = var.default_tags
  }
}
