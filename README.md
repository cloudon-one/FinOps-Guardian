# GCP & AWS FinOps Tools

1. GCP Organization Recommender – a serverless solution to monitor and receive Google Cloud Platform (GCP) recommendations across your organization.
2. AWS Resource Cleanup – an automated solution for cleaning up unused Amazon Web Services (AWS) resources across multiple regions.

Both solutions aim to reduce costs and optimize resource usage in their respective clouds, each leveraging native cloud services for monitoring, notifications, and remediation actions.

## 1. GCP Organization Recommender

A serverless solution that periodically checks for GCP recommendations using Google Cloud's Recommender API and delivers alerts (e.g., Slack notifications) about cost savings and optimization opportunities.

### 1.1 Key Highlights

- Cost & Resource Optimization
  - Identifies idle or underutilized resources: VM instances, Cloud SQL instances, IP addresses, disks, and images
  - Provides right-sizing recommendations for VMs and Cloud SQL instances
  - Identifies spending patterns for commitment usage and other billing optimizations

- Slack Notifications
  - Sends real-time or scheduled alerts with recommendation details (cost impact, recommended action, etc.)

- Serverless & Automated
  - Uses Cloud Functions triggered by Cloud Scheduler (with Pub/Sub as an intermediary)
  - Fully automated checks at a configurable frequency

- Extensible
  - Easily add new recommenders by extending a base Recommender class
  - Manages multiple resource types in a single solution

### 1.2 Architecture

[![](https://mermaid.ink/img/pako:eNqNVWFvmzAQ_SsWk_aJSlPSShuTJtFk6VCTjYSsk0b6wTEGrICNjGnXlf73nYEkJnRtkUKC7-7d3bt35NEiIqKWY8WZuCcplgqtpxuO4CqrbSJxkaKNtZYsSajcWK1FX5MgnGSiilBAUhpVGZW3R6O_Dv1qG1RbtBYFI7dmGDo7-1J3gCinZYkTWkNE60N5tOGD_L4UBDwZT3olzLoSZhUnigneq6DJ8_WOcoVUm62GiJeyXE189EMmmLO_WMOhFS1FJSGzmTVikjbZ0PryeHqzCG8WyOOlwhwCjEqC5XzP1HJunE-94DqcsnJnOnuLq9DLgZHeoR96PnKjSAIHPculN5-HlyzLgBk0xQrfvtaf63tv6GblhitKRJ4DEEwJgoykrhu6UIc6OZ7MGsaXFZUPNSAMLHNWKoR1ZFkDiAnY2FtQxmNxDP-PHKjMGchB8Df0ErhhQOUdIxS5hIiKK5Nad_EIH7QSGS2fzKCmpG8YSgX7oJefMIcavAZVrtrAA3uNkMqj8ga9fBeKxYy0fmY3wdydXIdBhskO_aLbVIjdkO0AUiAMy6c5bSJe4i1QQoK2zCxXxz1ujc_kAANFcbdjSL8vah03yAQL8F6LHO5a3PAFctZ3H25aqh017VIh4Aa3QmjDSQbimNIYJaRAMYjaeXc--ngRn9ulkmJHTx7P7lmkUmdU_LGJyIR07lOm6OcTrLLtqsOLcTSKRgc8Oh4PwE4BuDGfDiUa0XFMXqvqFEju-96D6GIOIGPyeinFQfaHduiFgRF_-vAchoECr1_bX9uTmb1ybVg7YNpMoqe6Z6x33iirR0XPfLOwYey2HroNI7c9327GvW-5j-XaeuOOzTRWy7ZyOMEsgv-iR32ysVRKcxCrAz8jGuMqU1q5T-CKKyWCB04sR8mK2pYUVZJaToyzEp6qAqRFpwyD7vO9S4H5byHyzunpH9zPJeM?type=png)](https://mermaid.live/edit#pako:eNqNVWFvmzAQ_SsWk_aJSlPSShuTJtFk6VCTjYSsk0b6wTEGrICNjGnXlf73nYEkJnRtkUKC7-7d3bt35NEiIqKWY8WZuCcplgqtpxuO4CqrbSJxkaKNtZYsSajcWK1FX5MgnGSiilBAUhpVGZW3R6O_Dv1qG1RbtBYFI7dmGDo7-1J3gCinZYkTWkNE60N5tOGD_L4UBDwZT3olzLoSZhUnigneq6DJ8_WOcoVUm62GiJeyXE189EMmmLO_WMOhFS1FJSGzmTVikjbZ0PryeHqzCG8WyOOlwhwCjEqC5XzP1HJunE-94DqcsnJnOnuLq9DLgZHeoR96PnKjSAIHPculN5-HlyzLgBk0xQrfvtaf63tv6GblhitKRJ4DEEwJgoykrhu6UIc6OZ7MGsaXFZUPNSAMLHNWKoR1ZFkDiAnY2FtQxmNxDP-PHKjMGchB8Df0ErhhQOUdIxS5hIiKK5Nad_EIH7QSGS2fzKCmpG8YSgX7oJefMIcavAZVrtrAA3uNkMqj8ga9fBeKxYy0fmY3wdydXIdBhskO_aLbVIjdkO0AUiAMy6c5bSJe4i1QQoK2zCxXxz1ujc_kAANFcbdjSL8vah03yAQL8F6LHO5a3PAFctZ3H25aqh017VIh4Aa3QmjDSQbimNIYJaRAMYjaeXc--ngRn9ulkmJHTx7P7lmkUmdU_LGJyIR07lOm6OcTrLLtqsOLcTSKRgc8Oh4PwE4BuDGfDiUa0XFMXqvqFEju-96D6GIOIGPyeinFQfaHduiFgRF_-vAchoECr1_bX9uTmb1ybVg7YNpMoqe6Z6x33iirR0XPfLOwYey2HroNI7c9327GvW-5j-XaeuOOzTRWy7ZyOMEsgv-iR32ysVRKcxCrAz8jGuMqU1q5T-CKKyWCB04sR8mK2pYUVZJaToyzEp6qAqRFpwyD7vO9S4H5byHyzunpH9zPJeM)

1. Cloud Function
   - Python 3.9 runtime
   - Invoked by Pub/Sub messages (scheduled via Cloud Scheduler)

2. Cloud Scheduler & Pub/Sub
   - Scheduler triggers the Pub/Sub topic on a defined cron schedule
   - Pub/Sub event invokes the Cloud Function

3. Service Account & IAM
   - Requires organization-level permissions to read recommender data across projects
   - Assign necessary roles/recommender.* for each resource type you want to check

4. Cloud Storage
   - Stores function code (Terraform can push code to the bucket during deployment)

### 1.3 Supported Recommenders

- Idle Resources
  - google.compute.instance.IdleResourceRecommender
  - google.compute.address.IdleResourceRecommender
  - google.compute.disk.IdleResourceRecommender
  - google.compute.image.IdleResourceRecommender
  - google.cloudsql.instance.IdleRecommender

- Right-sizing
  - google.compute.instance.MachineTypeRecommender
  - google.cloudsql.instance.OverprovisionedRecommender

- Cost Optimization
  - google.cloudbilling.commitment.SpendBasedCommitmentRecommender
  - google.compute.commitment.UsageCommitmentRecommender

### 1.4 Prerequisites & Required Permissions

- Deployment Permissions
  - roles/resourcemanager.organizationAdmin for Terraform setup

- Service Account Permissions
  - Must include roles such as:
    - roles/cloudasset.viewer
    - roles/recommender.computeViewer
    - roles/recommender.cloudsqlViewer
    - roles/recommender.billingAccountCudViewer
    - roles/recommender.ucsViewer
    - roles/recommender.projectCudViewer
    - (Optional) roles/recommender.firewallViewer, roles/recommender.iamViewer, etc.

- Required APIs
  - Cloud Asset API, Cloud Functions API, Cloud Scheduler API, Recommender API, and others

### 1.5 Configuration

Set environment variables to control which recommender checks are enabled and where notifications are sent:

```bash
ORGANIZATION_ID="<your-gcp-org-id>"
SLACK_HOOK_URL="<your-slack-webhook-url>"
IDLE_VM_RECOMMENDER_ENABLED="true"
IDLE_SQL_RECOMMENDER_ENABLED="true"
# ... etc.
```

### 1.6 Deployment & Notifications

- Terraform
  - Deploys all required resources (service account, IAM roles, Cloud Function, Pub/Sub topic, Cloud Scheduler job, etc.)

- Notifications
  - Slack messages are sent with project ID, recommendation type, action, cost impact, and more

### 1.7 Extensibility & Contributing

- To add a new recommender, create a new Python class extending the base Recommender class and integrate it into main.py
- Pull requests and contributions are welcome; ensure new recommenders follow the same architecture and patterns

## 2. AWS Resource Cleaner

An automated solution designed to identify and remove unused AWS resources across multiple regions. Reduces costs by cleaning up orphaned or unnecessary infrastructure components.

### 2.1 Key Highlights

- Multi-Region Resource Cleanup
  - Operates across specified or all AWS regions, making it flexible for multi-region deployments

- Comprehensive Coverage
  - Stops or deletes resources like EC2 instances, EBS volumes, EKS node groups, RDS instances, load balancers, Kinesis streams, MSK clusters, and more

- Scheduled via CloudWatch Events
  - Automate daily or weekly cleanup with a CRON expression

- Email Notifications
  - Sends a comprehensive summary of the cleanup to an SES-verified email address

- Safety Features
  - Dry Run Mode: Evaluate the cleanup actions without actually deleting any resources
  - Tag-Based Preservation: Skip resources tagged with a specified key-value pair
  - Spot Instance Protection: Excludes spot instances from termination

### 2.2 Architecture

[![](https://mermaid.ink/img/pako:eNqVVUuP2jAQ_itWDj0tPfTIoVI3pFsEu0WEdqU1HEwyJFYdO_JjK7Tsf-84hiQsNO1GSuaR-eblsf0SZSqHaBzthPqdlUxbspqsJcHHuG2hWV2SleZFAdoEtX_iRxoL5fJHZrOSJM8grdmQ0ejzIc1KyJ2AE-hA5qza5ixgQeZr-cZ7rDTQdfTlMSVLMMrpDEgsgElXn7DRpgsdVDQQ8tXJzHIlQ_C4hOzXAT3KHS962TYyDcRp5gGksQ2whVYZGHNo4_cqbVW0Te4bk7kAvRkqyUfyxGolet4mer90kiIhSMk9tr5X2ooVTVYUmdGWGcjJQoMB_dykvOlnVaAiGAf-WM_bUORD6xXZHoyMPmLlU7kTDmQGF7VfK6vtwGpfX-1RWISwdgeSxJ8ovt3vzT8hy0lK8X0PJJmlFN_3QFKrgVU0EC4LkmKL-f9BgemspN9rkIEdmIKz2jvPXt3sFKvQ4VQay2QzX05Kn0yr2VxiJtywrcDVuleSW6XRnk7AMi5wVjrdFeQSsASDyGS6oIlgxvKMTBdXg6Cp9Za3Kf0hmbXM72nyUwlXXc1qCZV6RsD8liZVbfdkrlhObpnwZWgz0KKzte41H9Vdi1DyPRls0AUiFs5Y0C3oKA8lczZFvSpnR9cZ851_wD17p5WrDfUsCTyxijyBVgPuL8etixH-nXV_xiUYbnAFnD8IjuJmEHOfzk72yA7l0sxuz1cjn_maqIpx2cY_igM-H5TlO541R9VfD4cl1Epb3EdJSv2Jj7RfUnJsNfrH-cOIgjbfc-cDSXR74GoG_sybqwKviPb26l9k-KvnPLqJKtAYPsfr8cWr15EtoYJ1NEY2hx1zwq6jtXxFU-asSvcyi8ZWO7iJcCyKMhrvmDAouTpnFiacYZrVyaRm8kmp6mj0-geaFHhj?type=png)](https://mermaid.live/edit#pako:eNqVVUuP2jAQ_itWDj0tPfTIoVI3pFsEu0WEdqU1HEwyJFYdO_JjK7Tsf-84hiQsNO1GSuaR-eblsf0SZSqHaBzthPqdlUxbspqsJcHHuG2hWV2SleZFAdoEtX_iRxoL5fJHZrOSJM8grdmQ0ejzIc1KyJ2AE-hA5qza5ixgQeZr-cZ7rDTQdfTlMSVLMMrpDEgsgElXn7DRpgsdVDQQ8tXJzHIlQ_C4hOzXAT3KHS962TYyDcRp5gGksQ2whVYZGHNo4_cqbVW0Te4bk7kAvRkqyUfyxGolet4mer90kiIhSMk9tr5X2ooVTVYUmdGWGcjJQoMB_dykvOlnVaAiGAf-WM_bUORD6xXZHoyMPmLlU7kTDmQGF7VfK6vtwGpfX-1RWISwdgeSxJ8ovt3vzT8hy0lK8X0PJJmlFN_3QFKrgVU0EC4LkmKL-f9BgemspN9rkIEdmIKz2jvPXt3sFKvQ4VQay2QzX05Kn0yr2VxiJtywrcDVuleSW6XRnk7AMi5wVjrdFeQSsASDyGS6oIlgxvKMTBdXg6Cp9Za3Kf0hmbXM72nyUwlXXc1qCZV6RsD8liZVbfdkrlhObpnwZWgz0KKzte41H9Vdi1DyPRls0AUiFs5Y0C3oKA8lczZFvSpnR9cZ851_wD17p5WrDfUsCTyxijyBVgPuL8etixH-nXV_xiUYbnAFnD8IjuJmEHOfzk72yA7l0sxuz1cjn_maqIpx2cY_igM-H5TlO541R9VfD4cl1Epb3EdJSv2Jj7RfUnJsNfrH-cOIgjbfc-cDSXR74GoG_sybqwKviPb26l9k-KvnPLqJKtAYPsfr8cWr15EtoYJ1NEY2hx1zwq6jtXxFU-asSvcyi8ZWO7iJcCyKMhrvmDAouTpnFiacYZrVyaRm8kmp6mj0-geaFHhj)

1. Lambda Function
   - Python 3.9 code implementing the cleanup logic

2. CloudWatch Events (EventBridge)
   - Scheduled trigger to run the Lambda at a defined frequency

3. SES (Simple Email Service)
   - Delivers email notifications of resources cleaned or skipped

4. IAM
   - Requires adequate permissions (e.g., describe/delete resources, manage tags, etc.)

### 2.3 Prerequisites

- AWS Account with the relevant IAM permissions
- Terraform for deployment
- Python 3.9 runtime support in Lambda
- Configured AWS Credentials (e.g., via ~/.aws/credentials)

### 2.4 Configuration

Environment variables in the Lambda function:

```bash
CHECK_ALL_REGIONS="false"        # or true
KEEP_TAG_KEY="auto-deletion"     # resources with this key are preserved
DRY_RUN="true"                   # set to "false" for actual deletions
EMAIL_IDENTITY="your-email@domain.com"
TO_ADDRESS="notifications@domain.com"
```

### 2.5 Resource Handling Overview

- EC2 Instances
  - Stops running On-Demand instances
  - Disables detailed monitoring

- Elastic IP Addresses
  - Releases unassociated EIPs

- EBS Volumes
  - Deletes unattached volumes; optionally preserves certain volumes (e.g., EKS)

- Load Balancers
  - Removes empty classic load balancers

- RDS (Instances & Clusters)
  - Stops running instances/clusters with concurrency support

- EKS Node Groups
  - Scales node groups to zero while preserving cluster configuration

- Kinesis & MSK
  - Deletes unused Kinesis streams or MSK clusters

- OpenSearch
  - Deletes unused domains

- Resource Tagging
  - Supports adding CreatedOn or other tags for auditing or skip logic

### 2.6 Email Notifications

Detailed summary of:

- Successfully Deleted resources
- Skipped resources (e.g., preserved by tag or in error state)
- Errors/Failures

### 2.7 Deployment

1. Configure variables in terraform.tfvars:

```hcl
function_name     = "aws-resource-cleanup"
check_all_regions = false
keep_tag_key      = { "auto-deletion" = "skip-resource" }
dry_run           = true
email_identity    = "your-email@domain.com"
to_address        = "notifications@domain.com"
event_cron        = "cron(0 20 * * ? *)"  # 8 PM GMT
```

2. Run Terraform to deploy:

```bash
terraform init
terraform plan
terraform apply
```

### 2.8 Best Practices

- Start with dry_run = true to verify logs and email reports before performing actual deletions
- Tag critical resources with the preserve tag (e.g., auto-deletion=skip-resource)
- Monitor CloudWatch Logs for Lambda execution details
- Ensure email_identity is verified in SES
- Regularly review the email notifications to stay informed on cleanup results

## 3. Combined Most Important Features

- Automated Cost Optimization
  - GCP: Uses Recommender API for cost-saving suggestions (idle resources, right-sizing, billing optimization)
  - AWS: Cleans up unused resources (EC2, EBS, RDS, EKS, Kinesis, MSK, etc.) to reduce costs

- Serverless & Scheduled
  - GCP: Cloud Functions triggered via Cloud Scheduler
  - AWS: Lambda function triggered via CloudWatch Events

- Notifications & Reporting
  - GCP: Slack alerts on potential savings and recommended actions
  - AWS: Email reports summarizing cleanup actions

- Safety & Control
  - GCP: Granular control via environment variables, easy to enable/disable checks
  - AWS: Dry run mode, preserve tags, multi-region checks, concurrency controls

## 4. License

Both projects are available under the MIT License. For details, see their respective LICENSE files.

## Contributions & Support

- GCP Organization Recommender:
Feel free to open PRs or issues in the GCP FinOps Recommender Repo. Remember to follow the recommended structure for new recommenders.

- AWS Resource Cleanup:
Contributions are welcome in the AWS Resource Cleanup Repo. Please ensure you test thoroughly in dry run mode before committing changes.

Happy Cloud Optimizing!