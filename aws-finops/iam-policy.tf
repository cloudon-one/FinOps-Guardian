# Least-privilege IAM policy for Lambda resource cleanup function

data "aws_iam_policy_document" "lambda_cleanup_policy" {
  # EC2 permissions
  statement {
    sid    = "EC2ReadWrite"
    effect = "Allow"
    actions = [
      "ec2:DescribeInstances",
      "ec2:DescribeRegions",
      "ec2:DescribeVolumes",
      "ec2:DescribeAddresses",
      "ec2:StopInstances",
      "ec2:DeleteVolume",
      "ec2:ReleaseAddress",
      "ec2:UnmonitorInstances",
      "ec2:CreateTags"
    ]
    resources = ["*"]
  }

  # Load Balancer permissions
  statement {
    sid    = "ELBReadWrite"
    effect = "Allow"
    actions = [
      "elasticloadbalancing:DescribeLoadBalancers",
      "elasticloadbalancing:DeleteLoadBalancer"
    ]
    resources = ["*"]
  }

  # RDS permissions
  statement {
    sid    = "RDSReadWrite"
    effect = "Allow"
    actions = [
      "rds:DescribeDBInstances",
      "rds:DescribeDBClusters",
      "rds:StopDBInstance",
      "rds:StopDBCluster"
    ]
    resources = ["*"]
  }

  # EKS permissions
  statement {
    sid    = "EKSReadWrite"
    effect = "Allow"
    actions = [
      "eks:ListClusters",
      "eks:DescribeCluster",
      "eks:ListNodegroups",
      "eks:DescribeNodegroup",
      "eks:UpdateNodegroupConfig"
    ]
    resources = ["*"]
  }

  # Kinesis permissions
  statement {
    sid    = "KinesisReadWrite"
    effect = "Allow"
    actions = [
      "kinesis:ListStreams",
      "kinesis:DeleteStream"
    ]
    resources = ["*"]
  }

  # MSK (Kafka) permissions
  statement {
    sid    = "MSKReadWrite"
    effect = "Allow"
    actions = [
      "kafka:ListClusters",
      "kafka:DeleteCluster"
    ]
    resources = ["*"]
  }

  # OpenSearch permissions
  statement {
    sid    = "OpenSearchReadWrite"
    effect = "Allow"
    actions = [
      "es:ListDomainNames",
      "es:DeleteDomain",
      "es:DescribeDomain"
    ]
    resources = ["*"]
  }

  # AWS Config permissions (for resource tagging)
  statement {
    sid    = "ConfigRead"
    effect = "Allow"
    actions = [
      "config:GetResourceConfigHistory",
      "config:GetDiscoveredResourceCounts"
    ]
    resources = ["*"]
  }

  # SES permissions (for email notifications)
  statement {
    sid    = "SESEmail"
    effect = "Allow"
    actions = [
      "ses:SendEmail",
      "ses:SendRawEmail",
      "ses:GetIdentityVerificationAttributes"
    ]
    resources = ["*"]
  }

  # CloudWatch Logs permissions (Lambda default)
  statement {
    sid    = "CloudWatchLogs"
    effect = "Allow"
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]
    resources = ["arn:aws:logs:*:*:*"]
  }
}

resource "aws_iam_policy" "lambda_cleanup_policy" {
  name        = "${var.function_name}-policy"
  description = "Least-privilege policy for AWS resource cleanup Lambda function"
  policy      = data.aws_iam_policy_document.lambda_cleanup_policy.json
}
