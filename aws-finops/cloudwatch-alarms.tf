# CloudWatch Alarms for Lambda monitoring and alerting

# Alarm for Lambda errors
resource "aws_cloudwatch_metric_alarm" "lambda_errors" {
  alarm_name          = "${var.function_name}-errors"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "Errors"
  namespace           = "AWS/Lambda"
  period              = "300"
  statistic           = "Sum"
  threshold           = "0"
  alarm_description   = "Alert when Lambda function encounters errors"
  treat_missing_data  = "notBreaching"

  dimensions = {
    FunctionName = module.lambda_function.lambda_function_name
  }

  # Optional: Add SNS topic for notifications
  # alarm_actions = [aws_sns_topic.alerts.arn]
}

# Alarm for Lambda throttles
resource "aws_cloudwatch_metric_alarm" "lambda_throttles" {
  alarm_name          = "${var.function_name}-throttles"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "Throttles"
  namespace           = "AWS/Lambda"
  period              = "300"
  statistic           = "Sum"
  threshold           = "0"
  alarm_description   = "Alert when Lambda function is throttled"
  treat_missing_data  = "notBreaching"

  dimensions = {
    FunctionName = module.lambda_function.lambda_function_name
  }

  # Optional: Add SNS topic for notifications
  # alarm_actions = [aws_sns_topic.alerts.arn]
}

# Alarm for Lambda duration (approaching timeout)
resource "aws_cloudwatch_metric_alarm" "lambda_duration" {
  alarm_name          = "${var.function_name}-duration-warning"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "Duration"
  namespace           = "AWS/Lambda"
  period              = "300"
  statistic           = "Maximum"
  threshold           = "${var.function_timeout * 1000 * 0.9}"  # 90% of timeout in milliseconds
  alarm_description   = "Alert when Lambda duration approaches timeout (90% threshold)"
  treat_missing_data  = "notBreaching"

  dimensions = {
    FunctionName = module.lambda_function.lambda_function_name
  }

  # Optional: Add SNS topic for notifications
  # alarm_actions = [aws_sns_topic.alerts.arn]
}

# Alarm for concurrent executions (if approaching account limit)
resource "aws_cloudwatch_metric_alarm" "lambda_concurrent_executions" {
  alarm_name          = "${var.function_name}-concurrent-executions"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "ConcurrentExecutions"
  namespace           = "AWS/Lambda"
  period              = "60"
  statistic           = "Maximum"
  threshold           = "50"  # Adjust based on your concurrent execution limit
  alarm_description   = "Alert when concurrent executions are high"
  treat_missing_data  = "notBreaching"

  dimensions = {
    FunctionName = module.lambda_function.lambda_function_name
  }

  # Optional: Add SNS topic for notifications
  # alarm_actions = [aws_sns_topic.alerts.arn]
}

# Alarm for invocation failures (non-200 responses)
resource "aws_cloudwatch_metric_alarm" "lambda_invocation_failures" {
  alarm_name          = "${var.function_name}-invocation-failures"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "DeadLetterErrors"
  namespace           = "AWS/Lambda"
  period              = "300"
  statistic           = "Sum"
  threshold           = "0"
  alarm_description   = "Alert when Lambda fails to send messages to DLQ"
  treat_missing_data  = "notBreaching"

  dimensions = {
    FunctionName = module.lambda_function.lambda_function_name
  }

  # Optional: Add SNS topic for notifications
  # alarm_actions = [aws_sns_topic.alerts.arn]
}

# Output alarm ARNs
output "alarm_arns" {
  description = "ARNs of CloudWatch alarms"
  value = {
    errors                = aws_cloudwatch_metric_alarm.lambda_errors.arn
    throttles             = aws_cloudwatch_metric_alarm.lambda_throttles.arn
    duration              = aws_cloudwatch_metric_alarm.lambda_duration.arn
    concurrent_executions = aws_cloudwatch_metric_alarm.lambda_concurrent_executions.arn
    invocation_failures   = aws_cloudwatch_metric_alarm.lambda_invocation_failures.arn
    dlq_messages          = aws_cloudwatch_metric_alarm.dlq_messages.arn
  }
}
