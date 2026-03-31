<p align="center">
  <img src="https://img.shields.io/badge/GCP-Cloud_Functions-4285F4?style=for-the-badge&logo=google-cloud&logoColor=white" alt="GCP">
  <img src="https://img.shields.io/badge/AWS-Lambda-FF9900?style=for-the-badge&logo=amazon-web-services&logoColor=white" alt="AWS">
  <img src="https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Terraform-1.3+-7B42BC?style=for-the-badge&logo=terraform&logoColor=white" alt="Terraform">
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License">
</p>

# FinOps Guardian

Enterprise-grade multi-cloud FinOps automation toolkit for cost optimization across GCP and AWS.

| Solution | What it does | Cloud | Notification |
|----------|-------------|-------|-------------|
| [GCP FinOps Guardian](#gcp-finops-guardian) | Scans for cost optimization recommendations via Recommender API | GCP | Slack |
| [AWS Resource Cleanup](#aws-resource-cleanup) | Identifies and removes unused resources across regions | AWS | SES Email |

---

## Table of Contents

- [GCP FinOps Guardian](#gcp-finops-guardian)
  - [Architecture](#gcp-architecture)
  - [Supported Recommenders](#supported-recommenders)
  - [Configuration](#gcp-configuration)
  - [Deployment](#gcp-deployment)
- [AWS Resource Cleanup](#aws-resource-cleanup)
  - [Architecture](#aws-architecture)
  - [Supported Resources](#supported-resources)
  - [Configuration](#aws-configuration)
  - [Deployment](#aws-deployment)
  - [Monitoring](#monitoring--observability)
- [Feature Comparison](#feature-comparison)
- [Getting Started](#getting-started)
- [Contributing](#contributing)
- [License](#license)

---

## GCP FinOps Guardian

Serverless solution that periodically checks for GCP recommendations using the Recommender API and delivers Slack alerts about cost savings. Supports both **organization-level** and **project-level** scanning.

| Feature | Detail |
|---------|--------|
| Runtime | Python 3.12 on Cloud Functions |
| Memory / Timeout | 512 MB / 300 s |
| Trigger | Cloud Scheduler → Pub/Sub → Cloud Function |
| Notifications | Slack (direct webhook or via Secret Manager) |
| Recommenders | 10 types, individually toggleable |
| IaC | Terraform (Google provider ~> 5.0) |

### GCP Architecture

[![GCP Architecture](https://mermaid.ink/img/pako:eNqNVWFvmzAQ_SsWk_aJSlPSShuTJtFk6VCTjYSsk0b6wTEGrICNjGnXlf73nYEkJnRtkUKC7-7d3bt35NEiIqKWY8WZuCcplgqtpxuO4CqrbSJxkaKNtZYsSajcWK1FX5MgnGSiilBAUhpVGZW3R6O_Dv1qG1RbtBYFI7dmGDo7-1J3gCinZYkTWkNE60N5tOGD_L4UBDwZT3olzLoSZhUnigneq6DJ8_WOcoVUm62GiJeyXE189EMmmLO_WMOhFS1FJSGzmTVikjbZ0PryeHqzCG8WyOOlwhwCjEqC5XzP1HJunE-94DqcsnJnOnuLq9DLgZHeoR96PnKjSAIHPculN5-HlyzLgBk0xQrfvtaf63tv6GblhitKRJ4DEEwJgoykrhu6UIc6OZ7MGsaXFZUPNSAMLHNWKoR1ZFkDiAnY2FtQxmNxDP-PHKjMGchB8Df0ErhhQOUdIxS5hIiKK5Nad_EIH7QSGS2fzKCmpG8YSgX7oJefMIcavAZVrtrAA3uNkMqj8ga9fBeKxYy0fmY3wdydXIdBhskO_aLbVIjdkO0AUiAMy6c5bSJe4i1QQoK2zCxXxz1ujc_kAANFcbdjSL8vah03yAQL8F6LHO5a3PAFctZ3H25aqh017VIh4Aa3QmjDSQbimNIYJaRAMYjaeXc--ngRn9ulkmJHTx7P7lmkUmdU_LGJyIR07lOm6OcTrLLtqsOLcTSKRgc8Oh4PwE4BuDGfDiUa0XFMXqvqFEju-96D6GIOIGPyeinFQfaHduiFgRF_-vAchoECr1_bX9uTmb1ybVg7YNpMoqe6Z6x33iirR0XPfLOwYey2HroNI7c9327GvW-5j-XaeuOOzTRWy7ZyOMEsgv-iR32ysVRKcxCrAz8jGuMqU1q5T-CKKyWCB04sR8mK2pYUVZJaToyzEp6qAqRFpwyD7vO9S4H5byHyzunpH9zPJeM?type=png)](https://mermaid.live/edit#pako:eNqNVWFvmzAQ_SsWk_aJSlPSShuTJtFk6VCTjYSsk0b6wTEGrICNjGnXlf73nYEkJnRtkUKC7-7d3bt35NEiIqKWY8WZuCcplgqtpxuO4CqrbSJxkaKNtZYsSajcWK1FX5MgnGSiilBAUhpVGZW3R6O_Dv1qG1RbtBYFI7dmGDo7-1J3gCinZYkTWkNE60N5tOGD_L4UBDwZT3olzLoSZhUnigneq6DJ8_WOcoVUm62GiJeyXE189EMmmLO_WMOhFS1FJSGzmTVikjbZ0PryeHqzCG8WyOOlwhwCjEqC5XzP1HJunE-94DqcsnJnOnuLq9DLgZHeoR96PnKjSAIHPculN5-HlyzLgBk0xQrfvtaf63tv6GblhitKRJ4DEEwJgoykrhu6UIc6OZ7MGsaXFZUPNSAMLHNWKoR1ZFkDiAnY2FtQxmNxDP-PHKjMGchB8Df0ErhhQOUdIxS5hIiKK5Nad_EIH7QSGS2fzKCmpG8YSgX7oJefMIcavAZVrtrAA3uNkMqj8ga9fBeKxYy0fmY3wdydXIdBhskO_aLbVIjdkO0AUiAMy6c5bSJe4i1QQoK2zCxXxz1ujc_kAANFcbdjSL8vah03yAQL8F6LHO5a3PAFctZ3H25aqh017VIh4Aa3QmjDSQbimNIYJaRAMYjaeXc--ngRn9ulkmJHTx7P7lmkUmdU_LGJyIR07lOm6OcTrLLtqsOLcTSKRgc8Oh4PwE4BuDGfDiUa0XFMXqvqFEju-96D6GIOIGPyeinFQfaHduiFgRF_-vAchoECr1_bX9uTmb1ybVg7YNpMoqe6Z6x33iirR0XPfLOwYey2HroNI7c9327GvW-5j-XaeuOOzTRWy7ZyOMEsgv-iR32ysVRKcxCrAz8jGuMqU1q5T-CKKyWCB04sR8mK2pYUVZJaToyzEp6qAqRFpwyD7vO9S4H5byHyzunpH9zPJeM)

**Components:** Cloud Scheduler → Pub/Sub → Cloud Function → Recommender API → Slack

| Component | Purpose |
|-----------|---------|
| Cloud Function | Runs recommendation checks (Python 3.12, factory pattern) |
| Cloud Scheduler + Pub/Sub | Triggers on configurable cron schedule |
| Service Account + IAM | Org-level or project-level least-privilege access |
| Cloud Storage | Versioned bucket for function code archives |
| Secret Manager *(optional)* | Secure storage for Slack webhook URL |

### Supported Recommenders

All 10 are enabled by default and individually toggleable via environment variables.

| Category | Recommender ID | Detects |
|----------|---------------|---------|
| **Idle Resources** | `google.compute.instance.IdleResourceRecommender` | Idle VM instances |
| | `google.compute.disk.IdleResourceRecommender` | Idle persistent disks |
| | `google.compute.image.IdleResourceRecommender` | Unused custom images |
| | `google.compute.address.IdleResourceRecommender` | Idle static IP addresses |
| | `google.cloudsql.instance.IdleRecommender` | Idle Cloud SQL instances |
| **Right-Sizing** | `google.compute.instance.MachineTypeRecommender` | VM instance right-sizing |
| | `google.compute.instanceGroupManager.MachineTypeRecommender` | MIG machine type optimization |
| | `google.cloudsql.instance.OverprovisionedRecommender` | Cloud SQL right-sizing |
| **Cost Optimization** | `google.compute.commitment.UsageCommitmentRecommender` | Usage-based CUD recommendations |
| | `google.cloudbilling.commitment.SpendBasedCommitmentRecommender` | Spend-based cost savings |

### GCP Configuration

<details>
<summary><b>Required Variables</b></summary>

| Variable | Description | Default |
|----------|-------------|---------|
| `GCP_PROJECT` | Project where function is deployed | *(required)* |
| `SCAN_SCOPE` | `"organization"` or `"project"` | `"project"` |
| `ORGANIZATION_ID` | GCP Org ID (required if scope = organization) | `""` |
| `SLACK_HOOK_URL` | Slack webhook URL (if not using Secret Manager) | *(required)* |

</details>

<details>
<summary><b>Optional Variables</b></summary>

| Variable | Description | Default |
|----------|-------------|---------|
| `MIN_COST_THRESHOLD` | Skip recommendations below this USD value | `0` |
| `USE_SECRET_MANAGER` | Use Secret Manager for webhook | `"false"` |
| `SLACK_WEBHOOK_SECRET_NAME` | Secret Manager resource name | `""` |

</details>

<details>
<summary><b>Recommender Toggles</b> (all default to <code>true</code>)</summary>

| Variable | Resource |
|----------|----------|
| `IDLE_VM_RECOMMENDER_ENABLED` | VM instances |
| `IDLE_DISK_RECOMMENDER_ENABLED` | Persistent disks |
| `IDLE_IMAGE_RECOMMENDER_ENABLED` | Custom images |
| `IDLE_IP_RECOMMENDER_ENABLED` | Static IPs |
| `IDLE_SQL_RECOMMENDER_ENABLED` | Cloud SQL instances |
| `RIGHTSIZE_VM_RECOMMENDER_ENABLED` | VM right-sizing |
| `RIGHTSIZE_SQL_RECOMMENDER_ENABLED` | Cloud SQL right-sizing |
| `MIG_RIGHTSIZE_RECOMMENDER_ENABLED` | MIG machine types |
| `COMMITMENT_USE_RECOMMENDER_ENABLED` | CUD usage |
| `BILLING_USE_RECOMMENDER_ENABLED` | Billing optimization |

</details>

<details>
<summary><b>IAM Roles</b> (automatically assigned by Terraform)</summary>

| Role | Purpose |
|------|---------|
| `roles/cloudasset.viewer` | Asset inventory access |
| `roles/recommender.computeViewer` | Compute recommendations |
| `roles/recommender.cloudsqlViewer` | Cloud SQL recommendations |
| `roles/recommender.cloudAssetInsightsViewer` | Asset insights |
| `roles/recommender.billingAccountCudViewer` | Billing CUD recommendations |
| `roles/recommender.ucsViewer` | Unattended project recommendations |
| `roles/recommender.projectCudViewer` | Project-level CUD recommendations |
| `roles/storage.objectCreator` | Function code storage |

**Required APIs** (auto-enabled): Cloud Asset, Cloud Build, Cloud Functions, Cloud Scheduler, Recommender, Service Usage, Cloud Resource Manager, Secret Manager, Pub/Sub

</details>

### GCP Deployment

**Project-level scanning:**

```hcl
# terraform.tfvars
gcp_project        = "your-project-id"
gcp_region         = "us-central1"
recommender_bucket = "your-project-recommender"
scan_scope         = "project"
slack_webhook_url  = "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
job_schedule       = "0 0 * * *"   # daily at midnight
job_timezone       = "America/New_York"
```

**Organization-level scanning** — add:

```hcl
scan_scope      = "organization"
organization_id = "123456789012"
```

```bash
cd gcp-finops && terraform init && terraform plan && terraform apply
```

<details>
<summary><b>Deployed Resources</b></summary>

- Service Account with IAM roles (org or project level)
- Cloud Storage bucket (versioned, lifecycle-managed)
- Cloud Function (Python 3.12, 512 MB)
- Pub/Sub topic + Cloud Scheduler job
- Secret Manager resources *(if enabled)*
- All required API enablements

</details>

<details>
<summary><b>Slack Notification Format</b></summary>

Each message includes: GCP Project ID, recommendation type, recommended action, description, cost savings (with currency), and projection duration.

</details>

---

## AWS Resource Cleanup

Automated multi-region resource cleanup with dry-run safety, tag-based preservation, and comprehensive email reporting.

| Feature | Detail |
|---------|--------|
| Runtime | Python 3.12 on Lambda |
| Timeout | 300 s (configurable) |
| Trigger | EventBridge (configurable CRON) |
| Notifications | SES email reports |
| Resources | 11 resource types across all regions |
| IaC | Terraform (AWS provider ~> 5.0) |

### AWS Architecture

[![AWS Architecture](https://mermaid.ink/img/pako:eNqVVUuP2jAQ_itWDj0tPfTIoVI3pFsEu0WEdqU1HEwyJFYdO_JjK7Tsf-84hiQsNO1GSuaR-eblsf0SZSqHaBzthPqdlUxbspqsJcHHuG2hWV2SleZFAdoEtX_iRxoL5fJHZrOSJM8grdmQ0ejzIc1KyJ2AE-hA5qza5ixgQeZr-cZ7rDTQdfTlMSVLMMrpDEgsgElXn7DRpgsdVDQQ8tXJzHIlQ_C4hOzXAT3KHS962TYyDcRp5gGksQ2whVYZGHNo4_cqbVW0Te4bk7kAvRkqyUfyxGolet4mer90kiIhSMk9tr5X2ooVTVYUmdGWGcjJQoMB_dykvOlnVaAiGAf-WM_bUORD6xXZHoyMPmLlU7kTDmQGF7VfK6vtwGpfX-1RWISwdgeSxJ8ovt3vzT8hy0lK8X0PJJmlFN_3QFKrgVU0EC4LkmKL-f9BgemspN9rkIEdmIKz2jvPXt3sFKvQ4VQay2QzX05Kn0yr2VxiJtywrcDVuleSW6XRnk7AMi5wVjrdFeQSsASDyGS6oIlgxvKMTBdXg6Cp9Za3Kf0hmbXM72nyUwlXXc1qCZV6RsD8liZVbfdkrlhObpnwZWgz0KKzte41H9Vdi1DyPRls0AUiFs5Y0C3oKA8lczZFvSpnR9cZ851_wD17p5WrDfUsCTyxijyBVgPuL8etixH-nXV_xiUYbnAFnD8IjuJmEHOfzk72yA7l0sxuz1cjn_maqIpx2cY_igM-H5TlO541R9VfD4cl1Epb3EdJSv2Jj7RfUnJsNfrH-cOIgjbfc-cDSXR74GoG_sybqwKviPb26l9k-KvnPLqJKtAYPsfr8cWr15EtoYJ1NEY2hx1zwq6jtXxFU-asSvcyi8ZWO7iJcCyKMhrvmDAouTpnFiacYZrVyaRm8kmp6mj0-geaFHhj?type=png)](https://mermaid.live/edit#pako:eNqVVUuP2jAQ_itWDj0tPfTIoVI3pFsEu0WEdqU1HEwyJFYdO_JjK7Tsf-84hiQsNO1GSuaR-eblsf0SZSqHaBzthPqdlUxbspqsJcHHuG2hWV2SleZFAdoEtX_iRxoL5fJHZrOSJM8grdmQ0ejzIc1KyJ2AE-hA5qza5ixgQeZr-cZ7rDTQdfTlMSVLMMrpDEgsgElXn7DRpgsdVDQQ8tXJzHIlQ_C4hOzXAT3KHS962TYyDcRp5gGksQ2whVYZGHNo4_cqbVW0Te4bk7kAvRkqyUfyxGolet4mer90kiIhSMk9tr5X2ooVTVYUmdGWGcjJQoMB_dykvOlnVaAiGAf-WM_bUORD6xXZHoyMPmLlU7kTDmQGF7VfK6vtwGpfX-1RWISwdgeSxJ8ovt3vzT8hy0lK8X0PJJmlFN_3QFKrgVU0EC4LkmKL-f9BgemspN9rkIEdmIKz2jvPXt3sFKvQ4VQay2QzX05Kn0yr2VxiJtywrcDVuleSW6XRnk7AMi5wVjrdFeQSsASDyGS6oIlgxvKMTBdXg6Cp9Za3Kf0hmbXM72nyUwlXXc1qCZV6RsD8liZVbfdkrlhObpnwZWgz0KKzte41H9Vdi1DyPRls0AUiFs5Y0C3oKA8lczZFvSpnR9cZ851_wD17p5WrDfUsCTyxijyBVgPuL8etixH-nXV_xiUYbnAFnD8IjuJmEHOfzk72yA7l0sxuz1cjn_maqIpx2cY_igM-H5TlO541R9VfD4cl1Epb3EdJSv2Jj7RfUnJsNfrH-cOIgjbfc-cDSXR74GoG_sybqwKviPb26l9k-KvnPLqJKtAYPsfr8cWr15EtoYJ1NEY2hx1zwq6jtXxFU-asSvcyi8ZWO7iJcCyKMhrvmDAouTpnFiacYZrVyaRm8kmp6mj0-geaFHhj)

**Components:** EventBridge → Lambda → (EC2, RDS, EKS, ...) → SES Email Report

| Component | Purpose |
|-----------|---------|
| Lambda Function | Thread-safe resource cleanup with retry & paginators |
| EventBridge | Scheduled trigger (configurable CRON) |
| CloudWatch Alarms | Error, throttle, duration, DLQ monitoring |
| SQS Dead Letter Queue | Encrypted queue for failed invocations |
| SES | Email reports (configurable region) |
| IAM | Least-privilege, per-service granular permissions |

### Supported Resources

| Resource | Action | Protection | Concurrency |
|----------|--------|-----------|-------------|
| EC2 Instances | Stop | Tag + Spot exclusion | Sequential |
| EC2 Monitoring | Disable detailed monitoring | - | Sequential |
| Elastic IPs | Release unassociated | Tag | Sequential |
| EBS Volumes | Delete unattached | Tag + EKS cluster check | Sequential |
| Classic ELBs | Delete empty | Tag | Sequential |
| RDS Instances & Clusters | Stop (available only) | - | Threaded |
| EKS Node Groups | Scale to zero | - | Threaded |
| Kinesis Streams | Delete (`upsolver_*` preserved) | Prefix | Threaded |
| MSK Clusters | Delete (ACTIVE only) | State filter | Threaded |
| OpenSearch Domains | Delete (idle only) | State filter | Threaded |
| Resource Tags | Add `CreatedOn` | - | Threaded |

> **Safety:** All operations default to **dry-run mode**. Set `DRY_RUN=false` to perform actual changes.

### AWS Configuration

<details>
<summary><b>Environment Variables</b></summary>

| Variable | Description | Default |
|----------|-------------|---------|
| `DRY_RUN` | `"true"` for dry-run, `"false"` for actual deletions | `"true"` |
| `CHECK_ALL_REGIONS` | Scan all enabled AWS regions | `"false"` |
| `KEEP_TAG_KEY` | Tag key for resource preservation | `"auto-deletion"` |
| `KEEP_TAG_VALUE` | Tag value for resource preservation | `"skip-resource"` |
| `EMAIL_IDENTITY` | SES verified sender email | *(required)* |
| `TO_ADDRESS` | Recipient email address | *(required)* |
| `SES_REGION` | AWS region where SES identity is verified | `"us-east-1"` |

</details>

<details>
<summary><b>Default Regions</b> (when <code>CHECK_ALL_REGIONS=false</code>)</summary>

`us-east-1`, `us-east-2`, `us-west-1`, `us-west-2`, `eu-north-1`, `eu-central-1`, `eu-west-1`

</details>

### AWS Deployment

```hcl
# terraform.tfvars
function_name     = "aws-resource-cleanup"
dry_run           = true
check_all_regions = false
keep_tag_key      = { "auto-deletion" = "skip-resource" }
email_identity    = "your-sender@domain.com"
to_address        = "your-recipient@domain.com"
ses_region        = "us-east-1"
event_cron        = "cron(0 23 * * ? *)"    # 11 PM UTC
sns_topic_arn     = ""                       # optional: SNS ARN for alarm notifications
```

```bash
cd aws-finops && terraform init && terraform plan && terraform apply
```

<details>
<summary><b>Deployed Resources</b></summary>

- Lambda function (Python 3.12) with least-privilege IAM
- EventBridge rule for scheduling
- Encrypted SQS Dead Letter Queue
- 6 CloudWatch alarms (with optional SNS)
- SES email identity verification

</details>

### Monitoring & Observability

| Alarm | Metric | Threshold |
|-------|--------|-----------|
| Errors | `AWS/Lambda Errors` | > 0 |
| Throttles | `AWS/Lambda Throttles` | > 0 |
| Duration | `AWS/Lambda Duration` | > 90% of timeout |
| Concurrent Executions | `AWS/Lambda ConcurrentExecutions` | > 50 |
| DLQ Delivery Failures | `AWS/Lambda DeadLetterErrors` | > 0 |
| DLQ Messages | `AWS/SQS ApproximateNumberOfMessagesVisible` | > 0 |

All alarms support optional SNS notifications via the `sns_topic_arn` variable.

**Email reports** include: deleted/stopped resources, skipped resources (dry-run or tagged), failed operations, and resources needing attention.

---

## Feature Comparison

| Capability | GCP FinOps Guardian | AWS Resource Cleanup |
|-----------|-------------------|---------------------|
| **Runtime** | Python 3.12 / Cloud Functions | Python 3.12 / Lambda |
| **IaC** | Terraform (Google ~> 5.0) | Terraform (AWS ~> 5.0) |
| **Trigger** | Cloud Scheduler + Pub/Sub | EventBridge CRON |
| **Notifications** | Slack (webhook / Secret Manager) | SES email reports |
| **Scope** | 10 recommender types | 11 resource cleanup types |
| **Concurrency** | Sequential per asset | ThreadPoolExecutor (5 workers) |
| **Safety** | Cost threshold filtering, per-recommender toggles | Dry-run mode, tag-based preservation, state filtering |
| **Credentials** | Optional Secret Manager | Configurable SES region |
| **Monitoring** | Cloud Logging + Slack | CloudWatch Alarms + optional SNS + DLQ |
| **IAM** | Least-privilege org/project roles | Least-privilege per-service policies |

---

## Getting Started

### Prerequisites

| | GCP | AWS |
|-|-----|-----|
| **Account** | GCP Organization or Project | AWS Account |
| **Terraform** | >= 1.3 (Google provider ~> 5.0) | >= 1.3 (AWS provider ~> 5.0) |
| **Python** | 3.12 | 3.12 |
| **Notification** | Slack webhook URL | SES verified email identity |

### Quick Start

```bash
# GCP
cd gcp-finops && terraform init && terraform apply

# AWS
cd aws-finops && terraform init && terraform apply
```

---

## Contributing

| Area | Guidelines |
|------|-----------|
| **GCP** | Follow factory pattern for new recommenders, maintain 80%+ test coverage, use structured logging |
| **AWS** | Test in dry-run mode first, follow modular function patterns, add error handling |
| **Both** | Update documentation, follow existing code patterns |

**Adding a new GCP recommender:**

1. Create class extending `Recommender` in `localpackage/recommender/compute/` or `cloudsql/`
2. Register in `factory.py`
3. Add Terraform variable in `variables.tf` + env var in `main.tf`

---

## License

MIT License. See [LICENSE](LICENSE) for details.

**Issues & Support:** [Open a GitHub issue](../../issues) with environment details and redacted logs.
