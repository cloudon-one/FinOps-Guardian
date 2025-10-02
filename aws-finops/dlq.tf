# Dead Letter Queue for failed Lambda executions

resource "aws_sqs_queue" "lambda_dlq" {
  name                      = "${var.function_name}-dlq"
  message_retention_seconds = 1209600  # 14 days
  visibility_timeout_seconds = 300

  tags = {
    Name        = "${var.function_name}-dlq"
    Purpose     = "Dead Letter Queue for failed Lambda executions"
    Environment = "production"
  }
}

# CloudWatch alarm for DLQ messages
resource "aws_cloudwatch_metric_alarm" "dlq_messages" {
  alarm_name          = "${var.function_name}-dlq-messages"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "ApproximateNumberOfMessagesVisible"
  namespace           = "AWS/SQS"
  period              = "300"
  statistic           = "Average"
  threshold           = "0"
  alarm_description   = "Alert when messages appear in DLQ"
  treat_missing_data  = "notBreaching"

  dimensions = {
    QueueName = aws_sqs_queue.lambda_dlq.name
  }

  # Optional: Add SNS topic for notifications
  # alarm_actions = [aws_sns_topic.alerts.arn]
}

# Output DLQ ARN for reference
output "dlq_arn" {
  description = "ARN of the Dead Letter Queue"
  value       = aws_sqs_queue.lambda_dlq.arn
}

output "dlq_url" {
  description = "URL of the Dead Letter Queue"
  value       = aws_sqs_queue.lambda_dlq.url
}
