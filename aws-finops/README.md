# AWS Resource Cleanup

An automated solution for cleaning up unused AWS resources across multiple regions to optimize costs. The project runs as a Lambda function that can be scheduled to execute regularly using CloudWatch Events.

## Overview

This project provides automated cleanup of various AWS resources:

- EC2 instances (stop running instances)
- EC2 detailed monitoring (disable)
- Elastic IP addresses (release unassociated)
- EBS volumes (delete unattached)
- Load balancers (delete empty)
- RDS instances and clusters (stop running)
- EKS node groups (scale to zero)
- Kinesis streams (delete unused)
- MSK clusters (delete unused)
- OpenSearch domains (delete unused)
- Resource tagging (add CreatedOn tags)

## Architecture
[![](https://mermaid.ink/img/pako:eNqVVUuP2jAQ_itWDj0tPfTIoVI3pFsEu0WEdqU1HEwyJFYdO_JjK7Tsf-84hiQsNO1GSuaR-eblsf0SZSqHaBzthPqdlUxbspqsJcHHuG2hWV2SleZFAdoEtX_iRxoL5fJHZrOSJM8grdmQ0ejzIc1KyJ2AE-hA5qza5ixgQeZr-cZ7rDTQdfTlMSVLMMrpDEgsgElXn7DRpgsdVDQQ8tXJzHIlQ_C4hOzXAT3KHS962TYyDcRp5gGksQ2whVYZGHNo4_cqbVW0Te4bk7kAvRkqyUfyxGolet4mer90kiIhSMk9tr5X2ooVTVYUmdGWGcjJQoMB_dykvOlnVaAiGAf-WM_bUORD6xXZHoyMPmLlU7kTDmQGF7VfK6vtwGpfX-1RWISwdgeSxJ8ovt3vzT8hy0lK8X0PJJmlFN_3QFKrgVU0EC4LkmKL-f9BgemspN9rkIEdmIKz2jvPXt3sFKvQ4VQay2QzX05Kn0yr2VxiJtywrcDVuleSW6XRnk7AMi5wVjrdFeQSsASDyGS6oIlgxvKMTBdXg6Cp9Za3Kf0hmbXM72nyUwlXXc1qCZV6RsD8liZVbfdkrlhObpnwZWgz0KKzte41H9Vdi1DyPRls0AUiFs5Y0C3oKA8lczZFvSpnR9cZ851_wD17p5WrDfUsCTyxijyBVgPuL8etixH-nXV_xiUYbnAFnD8IjuJmEHOfzk72yA7l0sxuz1cjn_maqIpx2cY_igM-H5TlO541R9VfD4cl1Epb3EdJSv2Jj7RfUnJsNfrH-cOIgjbfc-cDSXR74GoG_sybqwKviPb26l9k-KvnPLqJKtAYPsfr8cWr15EtoYJ1NEY2hx1zwq6jtXxFU-asSvcyi8ZWO7iJcCyKMhrvmDAouTpnFiacYZrVyaRm8kmp6mj0-geaFHhj?type=png)](https://mermaid.live/edit#pako:eNqVVUuP2jAQ_itWDj0tPfTIoVI3pFsEu0WEdqU1HEwyJFYdO_JjK7Tsf-84hiQsNO1GSuaR-eblsf0SZSqHaBzthPqdlUxbspqsJcHHuG2hWV2SleZFAdoEtX_iRxoL5fJHZrOSJM8grdmQ0ejzIc1KyJ2AE-hA5qza5ixgQeZr-cZ7rDTQdfTlMSVLMMrpDEgsgElXn7DRpgsdVDQQ8tXJzHIlQ_C4hOzXAT3KHS962TYyDcRp5gGksQ2whVYZGHNo4_cqbVW0Te4bk7kAvRkqyUfyxGolet4mer90kiIhSMk9tr5X2ooVTVYUmdGWGcjJQoMB_dykvOlnVaAiGAf-WM_bUORD6xXZHoyMPmLlU7kTDmQGF7VfK6vtwGpfX-1RWISwdgeSxJ8ovt3vzT8hy0lK8X0PJJmlFN_3QFKrgVU0EC4LkmKL-f9BgemspN9rkIEdmIKz2jvPXt3sFKvQ4VQay2QzX05Kn0yr2VxiJtywrcDVuleSW6XRnk7AMi5wVjrdFeQSsASDyGS6oIlgxvKMTBdXg6Cp9Za3Kf0hmbXM72nyUwlXXc1qCZV6RsD8liZVbfdkrlhObpnwZWgz0KKzte41H9Vdi1DyPRls0AUiFs5Y0C3oKA8lczZFvSpnR9cZ851_wD17p5WrDfUsCTyxijyBVgPuL8etixH-nXV_xiUYbnAFnD8IjuJmEHOfzk72yA7l0sxuz1cjn_maqIpx2cY_igM-H5TlO541R9VfD4cl1Epb3EdJSv2Jj7RfUnJsNfrH-cOIgjbfc-cDSXR74GoG_sybqwKviPb26l9k-KvnPLqJKtAYPsfr8cWr15EtoYJ1NEY2hx1zwq6jtXxFU-asSvcyi8ZWO7iJcCyKMhrvmDAouTpnFiacYZrVyaRm8kmp6mj0-geaFHhj)

- **Lambda Function**: Core cleanup logic implemented in Python
- **CloudWatch Events**: Scheduled trigger (defaults to nightly)
- **SES**: Email notifications for cleanup results
- **IAM**: Required permissions and policies
- **Multi-region Support**: Can operate across specified or all AWS regions

## Prerequisites

1. AWS account with appropriate permissions
2. Terraform installed
3. Python 3.9
4. Configured AWS credentials

## Configuration

### Environment Variables

- `CHECK_ALL_REGIONS`: Whether to check all AWS regions or only specified ones
- `KEEP_TAG_KEY`: Tag key to identify resources that should be preserved
- `DRY_RUN`: If true, shows what would be deleted without actually deleting
- `EMAIL_IDENTITY`: SES verified email for notifications
- `TO_ADDRESS`: Email address to receive cleanup notifications

### AWS Regions

Default regions covered:
- us-east-1
- us-east-2
- us-west-1
- us-west-2
- eu-central-1
- eu-west-1

## Resource Handling

### EC2 Instances
- Stops running non-spot instances
- Skips instances with specified preserve tags
- Disables detailed monitoring if enabled

### EBS Volumes
- Identifies and deletes unattached volumes
- Preserves volumes associated with EKS clusters
- Supports dry run mode

### Load Balancers
- Identifies and removes empty classic load balancers
- Includes error handling and reporting

### RDS
- Stops running instances and clusters
- Uses concurrent processing for efficiency
- Includes error handling

### EKS
- Scales node groups to zero
- Preserves cluster configuration
- Concurrent processing across regions

### Streaming Services
- Handles Kinesis streams (preserves upsolver_ prefixed streams)
- Removes MSK clusters
- Includes consumer deletion enforcement

### OpenSearch
- Removes OpenSearch domains
- Supports dry run mode
- Includes error handling

## Email Notifications

The system sends detailed email reports containing:
- Successfully deleted resources
- Skipped resources
- Resources that need attention
- Failed deletions

## Deployment

1. Configure variables in `terraform.tfvars`:
```hcl
function_name        = "aws-resource-cleanup"
check_all_regions    = false
keep_tag_key        = { "auto-deletion" = "skip-resource" }
dry_run             = true
email_identity      = "your-email@domain.com"
to_address         = "notifications@domain.com"
event_cron         = "cron(0 20 * * ? *)"  # 8 PM GMT
```

2. Initialize and apply Terraform:
```bash
terraform init
terraform plan
terraform apply
```

## Safety Features

1. Dry Run Mode: Test cleanup logic without actual deletions
2. Resource Tagging: Preserve tagged resources
3. Error Handling: Comprehensive error capture and reporting
4. Email Notifications: Detailed reports of all actions
5. Spot Instance Protection: Excludes spot instances from cleanup

## Monitoring and Logging

- CloudWatch Logs for Lambda execution
- Email notifications for cleanup results
- Error reporting and resource status tracking

## Best Practices

1. Always start with dry_run = true
2. Tag important resources with preserve tags
3. Monitor email notifications regularly
4. Review CloudWatch logs for detailed execution information
5. Maintain updated email verification in SES

## License

This project is licensed under the MIT License.