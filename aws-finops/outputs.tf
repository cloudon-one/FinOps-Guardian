# Consolidated outputs

output "lambda_function_arn" {
  description = "ARN of the Lambda function"
  value       = module.lambda_function.lambda_function_arn
}

output "lambda_function_name" {
  description = "Name of the Lambda function"
  value       = module.lambda_function.lambda_function_name
}

output "eventbridge_rule_arn" {
  description = "ARN of the EventBridge rule"
  value       = aws_cloudwatch_event_rule.nightly.arn
}

output "dlq_arn" {
  description = "ARN of the Dead Letter Queue"
  value       = aws_sqs_queue.lambda_dlq.arn
}

output "dlq_url" {
  description = "URL of the Dead Letter Queue"
  value       = aws_sqs_queue.lambda_dlq.url
}

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
