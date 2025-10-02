# FinOps Guardian

Enterprise-grade FinOps automation toolkit for multi-cloud cost optimization.

1. **GCP FinOps Guardian** – Serverless solution to monitor and receive Google Cloud Platform (GCP) recommendations across your organization or individual projects.
2. **AWS Resource Cleanup** – Automated solution for cleaning up unused Amazon Web Services (AWS) resources across multiple regions with comprehensive monitoring.

Both solutions aim to reduce costs and optimize resource usage in their respective clouds, each leveraging native cloud services for monitoring, notifications, and remediation actions.

## 1. GCP FinOps Guardian

A serverless solution that periodically checks for GCP recommendations using Google Cloud's Recommender API and delivers alerts (e.g., Slack notifications) about cost savings and optimization opportunities. Supports both organization-level and project-level scanning with flexible deployment options.

### 1.1 Key Highlights

- **Flexible Scanning Scope**
  - Organization-level scanning for multi-project environments
  - Project-level scanning for single projects
  - Easily switch between deployment modes

- **Cost & Resource Optimization**
  - Identifies idle or underutilized resources: VM instances, Cloud SQL instances, IP addresses, disks, and images
  - Right-sizing recommendations for VMs, Managed Instance Groups (MIG), and Cloud SQL instances
  - Spending patterns for commitment usage and billing optimizations
  - 10 different recommender types covering all major cost areas

- **Smart Notifications**
  - Slack integration with detailed cost impact information
  - Configurable minimum cost threshold to reduce noise
  - Real-time or scheduled alerts with recommendation details

- **Serverless & Automated**
  - Python 3.12 runtime with retry logic and exponential backoff
  - Cloud Functions triggered by Cloud Scheduler (with Pub/Sub)
  - Fully automated checks at configurable frequency
  - 512MB memory, 300-second timeout

- **Security & Best Practices**
  - Optional Secret Manager integration for credentials
  - Least-privilege IAM roles
  - Structured logging with distributed tracing
  - Comprehensive testing (92% code coverage)

- **Modern Architecture**
  - Factory pattern for dynamic recommender loading
  - Type-safe data models
  - Dependency injection design
  - Easily extensible for new recommender types

### 1.2 Architecture

[![](https://mermaid.ink/img/pako:eNqNVWFvmzAQ_SsWk_aJSlPSShuTJtFk6VCTjYSsk0b6wTEGrICNjGnXlf73nYEkJnRtkUKC7-7d3bt35NEiIqKWY8WZuCcplgqtpxuO4CqrbSJxkaKNtZYsSajcWK1FX5MgnGSiilBAUhpVGZW3R6O_Dv1qG1RbtBYFI7dmGDo7-1J3gCinZYkTWkNE60N5tOGD_L4UBDwZT3olzLoSZhUnigneq6DJ8_WOcoVUm62GiJeyXE189EMmmLO_WMOhFS1FJSGzmTVikjbZ0PryeHqzCG8WyOOlwhwCjEqC5XzP1HJunE-94DqcsnJnOnuLq9DLgZHeoR96PnKjSAIHPculN5-HlyzLgBk0xQrfvtaf63tv6GblhitKRJ4DEEwJgoykrhu6UIc6OZ7MGsaXFZUPNSAMLHNWKoR1ZFkDiAnY2FtQxmNxDP-PHKjMGchB8Df0ErhhQOUdIxS5hIiKK5Nad_EIH7QSGS2fzKCmpG8YSgX7oJefMIcavAZVrtrAA3uNkMqj8ga9fBeKxYy0fmY3wdydXIdBhskO_aLbVIjdkO0AUiAMy6c5bSJe4i1QQoK2zCxXxz1ujc_kAANFcbdjSL8vah03yAQL8F6LHO5a3PAFctZ3H25aqh017VIh4Aa3QmjDSQbimNIYJaRAMYjaeXc--ngRn9ulkmJHTx7P7lmkUmdU_LGJyIR07lOm6OcTrLLtqsOLcTSKRgc8Oh4PwE4BuDGfDiUa0XFMXqvqFEju-96D6GIOIGPyeinFQfaHduiFgRF_-vAchoECr1_bX9uTmb1ybVg7YNpMoqe6Z6x33iirR0XPfLOwYey2HroNI7c9327GvW-5j-XaeuOOzTRWy7ZyOMEsgv-iR32ysVRKcxCrAz8jGuMqU1q5T-CKKyWCB04sR8mK2pYUVZJaToyzEp6qAqRFpwyD7vO9S4H5byHyzunpH9zPJeM?type=png)](https://mermaid.live/edit#pako:eNqNVWFvmzAQ_SsWk_aJSlPSShuTJtFk6VCTjYSsk0b6wTEGrICNjGnXlf73nYEkJnRtkUKC7-7d3bt35NEiIqKWY8WZuCcplgqtpxuO4CqrbSJxkaKNtZYsSajcWK1FX5MgnGSiilBAUhpVGZW3R6O_Dv1qG1RbtBYFI7dmGDo7-1J3gCinZYkTWkNE60N5tOGD_L4UBDwZT3olzLoSZhUnigneq6DJ8_WOcoVUm62GiJeyXE189EMmmLO_WMOhFS1FJSGzmTVikjbZ0PryeHqzCG8WyOOlwhwCjEqC5XzP1HJunE-94DqcsnJnOnuLq9DLgZHeoR96PnKjSAIHPculN5-HlyzLgBk0xQrfvtaf63tv6GblhitKRJ4DEEwJgoykrhu6UIc6OZ7MGsaXFZUPNSAMLHNWKoR1ZFkDiAnY2FtQxmNxDP-PHKjMGchB8Df0ErhhQOUdIxS5hIiKK5Nad_EIH7QSGS2fzKCmpG8YSgX7oJefMIcavAZVrtrAA3uNkMqj8ga9fBeKxYy0fmY3wdydXIdBhskO_aLbVIjdkO0AUiAMy6c5bSJe4i1QQoK2zCxXxz1ujc_kAANFcbdjSL8vah03yAQL8F6LHO5a3PAFctZ3H25aqh017VIh4Aa3QmjDSQbimNIYJaRAMYjaeXc--ngRn9ulkmJHTx7P7lmkUmdU_LGJyIR07lOm6OcTrLLtqsOLcTSKRgc8Oh4PwE4BuDGfDiUa0XFMXqvqFEju-96D6GIOIGPyeinFQfaHduiFgRF_-vAchoECr1_bX9uTmb1ybVg7YNpMoqe6Z6x33iirR0XPfLOwYey2HroNI7c9327GvW-5j-XaeuOOzTRWy7ZyOMEsgv-iR32ysVRKcxCrAz8jGuMqU1q5T-CKKyWCB04sR8mK2pYUVZJaToyzEp6qAqRFpwyD7vO9S4H5byHyzunpH9zPJeM)

1. Cloud Function
   - Python 3.12 runtime with retry logic
   - 512MB memory, 300-second timeout
   - Invoked by Pub/Sub messages (scheduled via Cloud Scheduler)
   - Factory pattern for dynamic recommender loading
   - Structured logging with distributed tracing

2. Cloud Scheduler & Pub/Sub
   - Scheduler triggers the Pub/Sub topic on a defined cron schedule
   - Pub/Sub event invokes the Cloud Function
   - Configurable schedule and timezone

3. Service Account & IAM
   - Supports both organization-level and project-level permissions
   - Least-privilege IAM roles for recommender access
   - Assign necessary roles/recommender.* for each resource type

4. Cloud Storage
   - Stores function code (Terraform deploys code to bucket)
   - Uniform bucket-level access enabled

5. Secret Manager (Optional)
   - Secure storage for Slack webhook URL
   - Alternative to environment variable configuration

### 1.3 Supported Recommenders

The system supports 10 recommendation types (all enabled by default, individually configurable):

**Idle Resource Detection:**

- `google.compute.instance.IdleResourceRecommender` - Idle VM instances
- `google.compute.disk.IdleResourceRecommender` - Idle persistent disks
- `google.compute.image.IdleResourceRecommender` - Unused custom images
- `google.compute.address.IdleResourceRecommender` - Idle static IP addresses
- `google.cloudsql.instance.IdleRecommender` - Idle Cloud SQL instances

**Right-Sizing Recommendations:**

- `google.compute.instance.MachineTypeRecommender` - VM instance right-sizing
- `google.compute.instanceGroupManager.MachineTypeRecommender` - MIG machine type optimization
- `google.cloudsql.instance.OverprovisionedRecommender` - Cloud SQL right-sizing

**Cost Optimization:**

- `google.compute.commitment.UsageCommitmentRecommender` - Usage-based CUD recommendations
- `google.cloudbilling.commitment.SpendBasedCommitmentRecommender` - Spend-based cost savings

### 1.4 Prerequisites & Required Permissions

**Deployment Permissions:**

- For Organization-Level Scanning: `roles/resourcemanager.organizationAdmin`
- For Project-Level Scanning: `roles/owner` or equivalent project permissions

**Service Account Permissions** (automatically assigned by Terraform):

- Core Recommender Roles:
  - `roles/cloudasset.viewer` - Asset inventory access
  - `roles/recommender.computeViewer` - Compute recommendations
  - `roles/recommender.cloudsqlViewer` - Cloud SQL recommendations
  - `roles/recommender.cloudAssetInsightsViewer` - Asset insights
  - `roles/recommender.billingAccountCudViewer` - Billing CUD recommendations
  - `roles/recommender.ucsViewer` - Unattended project recommendations
  - `roles/recommender.projectCudViewer` - Project-level CUD recommendations
  - `roles/storage.objectCreator` - For storing results
- Additional Roles (optional):
  - `roles/recommender.productSuggestionViewer`, `roles/recommender.firewallViewer`, `roles/recommender.iamViewer`, etc.

**Required APIs** (automatically enabled by Terraform):

- Cloud Asset API, Cloud Build API, Cloud Functions API, Cloud Scheduler API, Recommender API, Service Usage API, Cloud Resource Manager API, Secret Manager API (optional)

### 1.5 Configuration

**Required Variables:**

```bash
GCP_PROJECT="your-project-id"                    # Project where function is deployed
SCAN_SCOPE="project"                             # "organization" or "project" (default: project)
ORGANIZATION_ID="123456789012"                   # Required if SCAN_SCOPE=organization
MIN_COST_THRESHOLD="0"                           # Minimum cost in USD to report (default: 0)
```

**Slack Notification (choose one method):**

```bash
# Method 1: Direct environment variable (default)
USE_SECRET_MANAGER="false"
SLACK_HOOK_URL="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"

# Method 2: Secret Manager (more secure)
USE_SECRET_MANAGER="true"
SLACK_WEBHOOK_SECRET_NAME="slack-webhook-secret"
```

**Recommender Toggles (all default to true):**

```bash
IDLE_VM_RECOMMENDER_ENABLED="true"               # VM idle resource detection
IDLE_DISK_RECOMMENDER_ENABLED="true"             # Disk idle resource detection
IDLE_IMAGE_RECOMMENDER_ENABLED="true"            # Image idle resource detection
IDLE_IP_RECOMMENDER_ENABLED="true"               # IP address idle detection
IDLE_SQL_RECOMMENDER_ENABLED="true"              # Cloud SQL idle detection
RIGHTSIZE_VM_RECOMMENDER_ENABLED="true"          # VM right-sizing recommendations
RIGHTSIZE_SQL_RECOMMENDER_ENABLED="true"         # Cloud SQL right-sizing
MIG_RIGHTSIZE_RECOMMENDER_ENABLED="true"         # MIG machine type optimization
COMMITMENT_USE_RECOMMENDER_ENABLED="true"        # CUD usage recommendations
BILLING_USE_RECOMMENDER_ENABLED="true"           # Billing optimization recommendations
```

### 1.6 Deployment

**Quick Start:**

1. Clone the repository and navigate to gcp-finops directory
2. Configure `terraform.tfvars`:

**For Project-Level Scanning:**

```hcl
gcp_project        = "your-project-id"
gcp_region         = "us-central1"
recommender_bucket = "your-project-recommender"
scan_scope         = "project"
slack_webhook_url  = "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
job_schedule       = "0 0 * * *"  # Daily at midnight
job_timezone       = "America/New_York"
```

**For Organization-Level Scanning:**

```hcl
gcp_project        = "your-project-id"
gcp_region         = "us-central1"
recommender_bucket = "your-project-recommender"
scan_scope         = "organization"
organization_id    = "123456789012"
slack_webhook_url  = "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
job_schedule       = "0 0 * * *"
job_timezone       = "America/New_York"
```

3. Deploy with Terraform:

```bash
terraform init
terraform plan
terraform apply
```

**Deployed Resources:**

- Service Account with IAM roles (org or project level)
- Cloud Storage bucket for function code
- Cloud Function (Python 3.12) with 512MB memory
- Pub/Sub topic for triggering
- Cloud Scheduler job for automation
- Secret Manager resources (if enabled)
- All required API enablements

### 1.7 Notifications

Slack messages include:

- GCP Project ID
- Recommendation type
- Recommended action
- Description
- Potential cost impact (with currency)
- Duration of the cost projection

### 1.8 Extensibility & Contributing

**Adding New Recommenders:**

1. Create a new class extending the base `Recommender` class
2. Register in `factory.py` for dynamic loading
3. Add Terraform variable in `variables.tf`
4. Add to Cloud Function environment in `main.tf`

**Testing:**

- Comprehensive test suite with 92% coverage
- Run tests: `pytest --cov=localpackage`

Contributions welcome! Follow existing patterns and maintain test coverage.

## 2. AWS Resource Cleaner

An automated solution designed to identify and remove unused AWS resources across multiple regions. Reduces costs by cleaning up orphaned or unnecessary infrastructure components with enterprise-grade monitoring and security.

### 2.1 Key Highlights

- **Multi-Region Resource Cleanup**
  - Operates across 7 default regions: us-east-1, us-east-2, us-west-1, us-west-2, eu-north-1, eu-central-1, eu-west-1
  - Support for all AWS regions with CHECK_ALL_REGIONS flag
  - Flexible for multi-region deployments

- **Comprehensive Coverage**
  - Stops or deletes: EC2 instances, EBS volumes, EKS node groups, RDS instances/clusters
  - Removes: Load balancers, Kinesis streams, MSK clusters, OpenSearch domains
  - Releases: Elastic IP addresses
  - Disables: EC2 detailed monitoring

- **Enterprise Monitoring & Reliability**
  - CloudWatch alarms for execution failures and throttling
  - Dead Letter Queue (DLQ) for failed invocations
  - SNS notifications for alarms
  - Python 3.12 runtime with retry logic

- **Security Best Practices**
  - Least-privilege IAM policy (replaced AdministratorAccess)
  - Granular permissions for each resource type
  - No overly permissive access

- **Scheduled via CloudWatch Events**
  - Automate daily or weekly cleanup with CRON expressions
  - EventBridge integration

- **Email Notifications**
  - Comprehensive summary via SES
  - Fixed sender address (aws@finsec.cloud)
  - Detailed deletion/skip/error reports

- **Safety Features**
  - Dry Run Mode: Evaluate actions without deleting
  - Tag-Based Preservation: Skip tagged resources
  - Spot Instance Protection: Excludes spot instances
  - Concurrent processing with error handling

### 2.2 Architecture

[![](https://mermaid.ink/img/pako:eNqVVUuP2jAQ_itWDj0tPfTIoVI3pFsEu0WEdqU1HEwyJFYdO_JjK7Tsf-84hiQsNO1GSuaR-eblsf0SZSqHaBzthPqdlUxbspqsJcHHuG2hWV2SleZFAdoEtX_iRxoL5fJHZrOSJM8grdmQ0ejzIc1KyJ2AE-hA5qza5ixgQeZr-cZ7rDTQdfTlMSVLMMrpDEgsgElXn7DRpgsdVDQQ8tXJzHIlQ_C4hOzXAT3KHS962TYyDcRp5gGksQ2whVYZGHNo4_cqbVW0Te4bk7kAvRkqyUfyxGolet4mer90kiIhSMk9tr5X2ooVTVYUmdGWGcjJQoMB_dykvOlnVaAiGAf-WM_bUORD6xXZHoyMPmLlU7kTDmQGF7VfK6vtwGpfX-1RWISwdgeSxJ8ovt3vzT8hy0lK8X0PJJmlFN_3QFKrgVU0EC4LkmKL-f9BgemspN9rkIEdmIKz2jvPXt3sFKvQ4VQay2QzX05Kn0yr2VxiJtywrcDVuleSW6XRnk7AMi5wVjrdFeQSsASDyGS6oIlgxvKMTBdXg6Cp9Za3Kf0hmbXM72nyUwlXXc1qCZV6RsD8liZVbfdkrlhObpnwZWgz0KKzte41H9Vdi1DyPRls0AUiFs5Y0C3oKA8lczZFvSpnR9cZ851_wD17p5WrDfUsCTyxijyBVgPuL8etixH-nXV_xiUYbnAFnD8IjuJmEHOfzk72yA7l0sxuz1cjn_maqIpx2cY_igM-H5TlO541R9VfD4cl1Epb3EdJSv2Jj7RfUnJsNfrH-cOIgjbfc-cDSXR74GoG_sybqwKviPb26l9k-KvnPLqJKtAYPsfr8cWr15EtoYJ1NEY2hx1zwq6jtXxFU-asSvcyi8ZWO7iJcCyKMhrvmDAouTpnFiacYZrVyaRm8kmp6mj0-geaFHhj?type=png)](https://mermaid.live/edit#pako:eNqVVUuP2jAQ_itWDj0tPfTIoVI3pFsEu0WEdqU1HEwyJFYdO_JjK7Tsf-84hiQsNO1GSuaR-eblsf0SZSqHaBzthPqdlUxbspqsJcHHuG2hWV2SleZFAdoEtX_iRxoL5fJHZrOSJM8grdmQ0ejzIc1KyJ2AE-hA5qza5ixgQeZr-cZ7rDTQdfTlMSVLMMrpDEgsgElXn7DRpgsdVDQQ8tXJzHIlQ_C4hOzXAT3KHS962TYyDcRp5gGksQ2whVYZGHNo4_cqbVW0Te4bk7kAvRkqyUfyxGolet4mer90kiIhSMk9tr5X2ooVTVYUmdGWGcjJQoMB_dykvOlnVaAiGAf-WM_bUORD6xXZHoyMPmLlU7kTDmQGF7VfK6vtwGpfX-1RWISwdgeSxJ8ovt3vzT8hy0lK8X0PJJmlFN_3QFKrgVU0EC4LkmKL-f9BgemspN9rkIEdmIKz2jvPXt3sFKvQ4VQay2QzX05Kn0yr2VxiJtywrcDVuleSW6XRnk7AMi5wVjrdFeQSsASDyGS6oIlgxvKMTBdXg6Cp9Za3Kf0hmbXM72nyUwlXXc1qCZV6RsD8liZVbfdkrlhObpnwZWgz0KKzte41H9Vdi1DyPRls0AUiFs5Y0C3oKA8lczZFvSpnR9cZ851_wD17p5WrDfUsCTyxijyBVgPuL8etixH-nXV_xiUYbnAFnD8IjuJmEHOfzk72yA7l0sxuz1cjn_maqIpx2cY_igM-H5TlO541R9VfD4cl1Epb3EdJSv2Jj7RfUnJsNfrH-cOIgjbfc-cDSXR74GoG_sybqwKviPb26l9k-KvnPLqJKtAYPsfr8cWr15EtoYJ1NEY2hx1zwq6jtXxFU-asSvcyi8ZWO7iJcCyKMhrvmDAouTpnFiacYZrVyaRm8kmp6mj0-geaFHhj)

1. **Lambda Function**
   - Python 3.12 runtime with retry logic
   - Modular cleanup logic for each resource type
   - Concurrent processing across regions
   - Error handling and reporting

2. **CloudWatch Events (EventBridge)**
   - Scheduled trigger (configurable CRON)
   - Automated execution at defined frequency

3. **CloudWatch Alarms & Monitoring**
   - Lambda execution failure alarms
   - Throttling detection alarms
   - SNS notifications for alerts
   - Comprehensive CloudWatch Logs

4. **Dead Letter Queue (DLQ)**
   - SQS DLQ for failed Lambda invocations
   - Captures failures for investigation
   - Prevents lost execution data

5. **SES (Simple Email Service)**
   - Email notifications with aws@finsec.cloud sender
   - Detailed reports: deleted, skipped, errors
   - Requires verified email identity

6. **IAM**
   - Least-privilege policy with granular permissions
   - Resource-specific access controls
   - No AdministratorAccess required

### 2.3 Prerequisites

- AWS Account with appropriate IAM permissions for Terraform deployment
- Terraform installed (version 1.0+)
- Python 3.12 runtime support in Lambda
- Configured AWS Credentials (e.g., via `~/.aws/credentials` or environment variables)
- SES verified email identity for notifications

### 2.4 Configuration

**Environment variables in the Lambda function:**

```bash
CHECK_ALL_REGIONS="false"                # or "true" to scan all AWS regions
KEEP_TAG_KEY="auto-deletion"             # resources with this key are preserved
DRY_RUN="true"                           # set to "false" for actual deletions
EMAIL_IDENTITY="aws@finsec.cloud"        # SES verified sender email
TO_ADDRESS="notifications@domain.com"    # recipient email address
```

**Default AWS Regions:**

- us-east-1 (N. Virginia)
- us-east-2 (Ohio)
- us-west-1 (N. California)
- us-west-2 (Oregon)
- eu-north-1 (Stockholm)
- eu-central-1 (Frankfurt)
- eu-west-1 (Ireland)

### 2.5 Resource Handling Overview

**EC2 Instances**

- Stops running On-Demand instances (spot instances excluded)
- Skips instances with preserve tags
- Disables detailed monitoring if enabled
- Concurrent processing with error handling

**Elastic IP Addresses**

- Releases unassociated EIPs
- Region-aware cleanup

**EBS Volumes**

- Deletes unattached volumes
- Preserves EKS-associated volumes
- Supports dry run mode

**Load Balancers**

- Identifies and removes empty classic load balancers
- Error handling and reporting

**RDS (Instances & Clusters)**

- Stops running instances and clusters
- Concurrent processing across regions
- Retry logic for API throttling

**EKS Node Groups**

- Scales node groups to zero
- Preserves cluster configuration
- Concurrent processing

**Kinesis Streams**

- Deletes unused streams
- Preserves streams with `upsolver_` prefix
- Consumer deletion enforcement

**MSK Clusters**

- Removes MSK clusters
- Error handling

**OpenSearch Domains**

- Deletes unused domains
- Supports dry run mode

**Resource Tagging**

- Adds CreatedOn tags for auditing
- Tag-based preservation logic

### 2.6 Email Notifications

**Email report includes:**

- Successfully deleted resources (by type and region)
- Skipped resources (preserved by tag or spot instances)
- Resources needing attention
- Failed deletions with error details
- Complete execution summary

### 2.7 Deployment

1. **Configure variables in `terraform.tfvars`:**

```hcl
function_name     = "aws-resource-cleanup"
check_all_regions = false
keep_tag_key      = { "auto-deletion" = "skip-resource" }
dry_run           = true
email_identity    = "aws@finsec.cloud"
to_address        = "notifications@domain.com"
event_cron        = "cron(0 20 * * ? *)"  # 8 PM GMT
```

2. **Run Terraform to deploy:**

```bash
cd aws-finops
terraform init
terraform plan
terraform apply
```

**Deployed Resources:**

- Lambda function (Python 3.12) with least-privilege IAM policy
- CloudWatch Event rule for scheduling
- SQS Dead Letter Queue for failed invocations
- CloudWatch alarms for monitoring
- SNS topic for alarm notifications
- SES email identity verification

### 2.8 Monitoring & Observability

**CloudWatch Alarms:**

- Lambda execution failures
- API throttling detection
- SNS notifications for critical issues

**CloudWatch Logs:**

- Detailed execution logs for each Lambda run
- Resource cleanup activity
- Error traces and debugging information

**Email Reports:**

- Daily/scheduled cleanup summaries
- Resource deletion confirmations
- Skip and error notifications

### 2.9 Best Practices

**Safety First:**

- Always start with `dry_run = true` to verify logs and email reports
- Review the email summary before enabling actual deletions
- Test in non-production environments first

**Resource Protection:**

- Tag critical resources with preserve tag (e.g., `auto-deletion=skip-resource`)
- Review tag strategy across your infrastructure
- Document tagged resources in your runbook

**Monitoring:**

- Monitor CloudWatch Logs for Lambda execution details
- Set up additional CloudWatch alarms based on your SLAs
- Review email notifications regularly

**SES Configuration:**

- Ensure `<your-email>` is verified in SES
- Configure SES for production sending limits
- Test email delivery before production use

**IAM Security:**

- Review the least-privilege IAM policy
- Audit permissions regularly
- Never use AdministratorAccess

## 3. Combined Key Features

### Automated Cost Optimization

- **GCP**: 10 recommender types using Recommender API for cost-saving suggestions (idle resources, right-sizing for VMs/MIG/SQL, billing optimization, CUD recommendations)
- **AWS**: Multi-region cleanup of unused resources (EC2, EBS, RDS, EKS, Kinesis, MSK, OpenSearch, EIPs)

### Modern Runtime & Architecture

- **GCP**: Python 3.12 runtime, factory pattern for dynamic loading, 92% test coverage
- **AWS**: Python 3.12 runtime, modular cleanup functions, retry logic with exponential backoff

### Serverless & Scheduled

- **GCP**: Cloud Functions (512MB, 5min timeout) triggered via Cloud Scheduler with Pub/Sub
- **AWS**: Lambda function triggered via CloudWatch Events with configurable CRON

### Notifications & Reporting

- **GCP**: Slack alerts with cost impact, minimum threshold filtering, structured logging
- **AWS**: SES email reports with aws@finsec.cloud sender, detailed deletion/skip/error summaries

### Security & Reliability

- **GCP**: Optional Secret Manager for credentials, least-privilege IAM roles, project or organization-level scanning
- **AWS**: Least-privilege IAM policy (no AdministratorAccess), CloudWatch alarms, Dead Letter Queue for failures

### Safety & Control

- **GCP**: Granular control via environment variables, 10 individual recommender toggles, min cost threshold
- **AWS**: Dry run mode, tag-based preservation, spot instance protection, concurrent processing with error handling

### Monitoring & Observability

- **GCP**: Structured Cloud Logging with distributed tracing, Cloud Monitoring metrics
- **AWS**: CloudWatch alarms for failures/throttling, SNS notifications, comprehensive logs

## 4. Getting Started

### Quick Links

- **GCP FinOps Guardian**: See [gcp-finops/README.md](gcp-finops/README.md) for detailed documentation
- **AWS Resource Cleanup**: See [aws-finops/README.md](aws-finops/README.md) for detailed documentation

### Prerequisites

**GCP:**

- GCP Organization or Project access
- Terraform 1.0+
- Python 3.12
- Slack webhook URL

**AWS:**

- AWS Account with appropriate permissions
- Terraform 1.0+
- Python 3.12
- SES verified email identity

## 5. Contributing

Contributions are welcome! Please:

**For GCP FinOps Guardian:**

- Follow the factory pattern for new recommenders
- Maintain 80%+ test coverage
- Update documentation (README, TESTING.md)
- Use structured logging with proper metadata

**For AWS Resource Cleanup:**
- Test thoroughly in dry run mode first
- Follow existing modular function patterns
- Add comprehensive error handling
- Document new resource types in README

## 6. License

Both projects are available under the MIT License. For details, see their respective LICENSE files.

## 7. Support

For issues, feature requests, or questions:

- Open a GitHub issue in this repository
- Provide detailed information about your environment
- Include relevant logs (redact sensitive information)

---

Happy Cloud Optimizing!

