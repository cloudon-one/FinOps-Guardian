# Provides an SES email identity resource
resource "aws_ses_email_identity" "email_identity" {
  email = var.email_identity
}

# Attaches a Managed IAM Policy to SES Email Identity resource
data "aws_iam_policy_document" "policy_document" {
  statement {
    actions   = ["ses:SendEmail", "ses:SendRawEmail"]
    resources = [aws_ses_email_identity.email_identity.arn]
  }
}

# Provides an IAM policy attached to a user.
resource "aws_iam_policy" "policy" {
  name   = var.iam_policy
  policy = data.aws_iam_policy_document.policy_document.json
}
