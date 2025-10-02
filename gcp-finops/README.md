# GCP FinOps Guardian

A serverless solution to monitor and receive GCP recommendations across your organization or individual projects. This system leverages Google Cloud's Recommender API to detect potential cost savings and optimization opportunities with automated notifications to Slack.

## Overview

This system runs as a Cloud Function that periodically checks for various types of recommendations across your GCP organization or individual projects and sends notifications to Slack. It supports both organization-level and project-level scanning, making it flexible for different deployment scenarios.

**Supported Resource Types:**
- Virtual Machines (GCE) - Idle detection and right-sizing
- Managed Instance Groups (MIG) - Machine type optimization
- Cloud SQL instances - Idle detection and right-sizing
- Persistent Disks - Idle resource identification
- Custom Images - Unused image detection
- Static IP Addresses - Idle IP detection
- Commitment usage - CUD recommendations
- Billing optimizations - Cost-saving opportunities

## Architecture

[![](https://mermaid.ink/img/pako:eNqNVWFvmzAQ_SsWk_aJSlPSShuTJtFk6VCTjYSsk0b6wTEGrICNjGnXlf73nYEkJnRtkUKC7-7d3bt35NEiIqKWY8WZuCcplgqtpxuO4CqrbSJxkaKNtZYsSajcWK1FX5MgnGSiilBAUhpVGZW3R6O_Dv1qG1RbtBYFI7dmGDo7-1J3gCinZYkTWkNE60N5tOGD_L4UBDwZT3olzLoSZhUnigneq6DJ8_WOcoVUm62GiJeyXE189EMmmLO_WMOhFS1FJSGzmTVikjbZ0PryeHqzCG8WyOOlwhwCjEqC5XzP1HJunE-94DqcsnJnOnuLq9DLgZHeoR96PnKjSAIHPculN5-HlyzLgBk0xQrfvtaf63tv6GblhitKRJ4DEEwJgoykrhu6UIc6OZ7MGsaXFZUPNSAMLHNWKoR1ZFkDiAnY2FtQxmNxDP-PHKjMGchB8Df0ErhhQOUdIxS5hIiKK5Nad_EIH7QSGS2fzKCmpG8YSgX7oJefMIcavAZVrtrAA3uNkMqj8ga9fBeKxYy0fmY3wdydXIdBhskO_aLbVIjdkO0AUiAMy6c5bSJe4i1QQoK2zCxXxz1ujc_kAANFcbdjSL8vah03yAQL8F6LHO5a3PAFctZ3H25aqh017VIh4Aa3QmjDSQbimNIYJaRAMYjaeXc--ngRn9ulkmJHTx7P7lmkUmdU_LGJyIR07lOm6OcTrLLtqsOLcTSKRgc8Oh4PwE4BuDGfDiUa0XFMXqvqFEju-96D6GIOIGPyeinFQfaHduiFgRF_-vAchoECr1_bX9uTmb1ybVg7YNpMoqe6Z6x33iirR0XPfLOwYey2HroNI7c9327GvW-5j-XaeuOOzTRWy7ZyOMEsgv-iR32ysVRKcxCrAz8jGuMqU1q5T-CKKyWCB04sR8mK2pYUVZJaToyzEp6qAqRFpwyD7vO9S4H5byHyzunpH9zPJeM?type=png)](https://mermaid.live/edit#pako:eNqNVWFvmzAQ_SsWk_aJSlPSShuTJtFk6VCTjYSsk0b6wTEGrICNjGnXlf73nYEkJnRtkUKC7-7d3bt35NEiIqKWY8WZuCcplgqtpxuO4CqrbSJxkaKNtZYsSajcWK1FX5MgnGSiilBAUhpVGZW3R6O_Dv1qG1RbtBYFI7dmGDo7-1J3gCinZYkTWkNE60N5tOGD_L4UBDwZT3olzLoSZhUnigneq6DJ8_WOcoVUm62GiJeyXE189EMmmLO_WMOhFS1FJSGzmTVikjbZ0PryeHqzCG8WyOOlwhwCjEqC5XzP1HJunE-94DqcsnJnOnuLq9DLgZHeoR96PnKjSAIHPculN5-HlyzLgBk0xQrfvtaf63tv6GblhitKRJ4DEEwJgoykrhu6UIc6OZ7MGsaXFZUPNSAMLHNWKoR1ZFkDiAnY2FtQxmNxDP-PHKjMGchB8Df0ErhhQOUdIxS5hIiKK5Nad_EIH7QSGS2fzKCmpG8YSgX7oJefMIcavAZVrtrAA3uNkMqj8ga9fBeKxYy0fmY3wdydXIdBhskO_aLbVIjdkO0AUiAMy6c5bSJe4i1QQoK2zCxXxz1ujc_kAANFcbdjSL8vah03yAQL8F6LHO5a3PAFctZ3H25aqh017VIh4Aa3QmjDSQbimNIYJaRAMYjaeXc--ngRn9ulkmJHTx7P7lmkUmdU_LGJyIR07lOm6OcTrLLtqsOLcTSKRgc8Oh4PwE4BuDGfDiUa0XFMXqvqFEju-96D6GIOIGPyeinFQfaHduiFgRF_-vAchoECr1_bX9uTmb1ybVg7YNpMoqe6Z6x33iirR0XPfLOwYey2HroNI7c9327GvW-5j-XaeuOOzTRWy7ZyOMEsgv-iR32ysVRKcxCrAz8jGuMqU1q5T-CKKyWCB04sR8mK2pYUVZJaToyzEp6qAqRFpwyD7vO9S4H5byHyzunpH9zPJeM)

The solution consists of the following components:

- **Cloud Function**: Runs the recommendation checks
- **Cloud Scheduler**: Triggers the function on a defined schedule
- **Pub/Sub**: Acts as an intermediary between the scheduler and function
- **Cloud Storage**: Stores the function code
- **Service Account**: Handles authentication and authorization

### Components Breakdown

1. **Service Account**:
   - Account ID: `organization-checker`
   - Assigned multiple IAM roles for accessing recommender services
   - Supports both organization-level and project-level permissions

2. **Cloud Function**:
   - Runtime: Python 3.12
   - Memory: 512MB
   - Timeout: 300 seconds (5 minutes)
   - Triggered by Pub/Sub messages
   - Structured logging to Cloud Logging with distributed tracing
   - Factory pattern for dynamic recommender loading

3. **Storage**:
   - GCS bucket for function source code
   - Uniform bucket level access enabled
   - Configurable location

4. **Cloud Scheduler**:
   - Configurable cron schedule (default: daily at midnight)
   - Retries configured with exponential backoff
   - Publishes to Pub/Sub topic for function triggering

5. **Secret Manager** (Optional):
   - Secure storage for Slack webhook URL
   - Alternative to environment variable configuration

## Supported Recommenders

The system supports 10 recommendation types (all enabled by default, individually configurable):

### Idle Resource Detection
- `google.compute.instance.IdleResourceRecommender` - Identifies idle VM instances
- `google.compute.disk.IdleResourceRecommender` - Identifies idle persistent disks
- `google.compute.image.IdleResourceRecommender` - Identifies unused custom images
- `google.compute.address.IdleResourceRecommender` - Identifies idle static IP addresses
- `google.cloudsql.instance.IdleRecommender` - Identifies idle Cloud SQL instances

### Right-Sizing Recommendations
- `google.compute.instance.MachineTypeRecommender` - VM instance right-sizing opportunities
- `google.compute.instanceGroupManager.MachineTypeRecommender` - MIG machine type optimization
- `google.cloudsql.instance.OverprovisionedRecommender` - Cloud SQL instance right-sizing

### Cost Optimization
- `google.compute.commitment.UsageCommitmentRecommender` - Usage-based CUD recommendations
- `google.cloudbilling.commitment.SpendBasedCommitmentRecommender` - Spend-based cost savings

## Features

### Core Capabilities
- **Flexible Scanning Scope**: Support for both organization-level and project-level scanning
- **Automated Detection**: 10 different types of cost optimization recommendations
- **Smart Notifications**: Slack integration with detailed cost impact information
- **Configurable Filtering**: Minimum cost threshold to reduce noise
- **Scheduled Execution**: Automated checks via Cloud Scheduler
- **Structured Logging**: Full observability with Cloud Logging integration
- **Factory Pattern**: Dynamic recommender loading based on configuration
- **Security**: Optional Secret Manager integration for webhook credentials
- **Retry Logic**: Exponential backoff for API resilience
- **Comprehensive Testing**: 92% code coverage with pytest

### Recommendation Categories

- **Idle Resources**:
  - VM instances
  - Cloud SQL instances
  - Persistent disks
  - Custom images
  - Static IP addresses

- **Right-sizing**:
  - VM instances
  - Managed Instance Groups (MIG)
  - Cloud SQL instances

- **Cost Optimization**:
  - Commitment usage recommendations (CUD)
  - Billing usage optimization

## Prerequisites

### Required Deployment Permissions

**For Organization-Level Scanning:**
- `roles/resourcemanager.organizationAdmin` - Required to grant organization-level IAM permissions

**For Project-Level Scanning:**
- `roles/owner` or equivalent project-level permissions to deploy Cloud Functions and configure IAM

### Required Service Account Permissions

The service account requires the following roles. Terraform automatically assigns these at either the organization or project level based on your `scan_scope` configuration:

#### Core Recommender Roles
- `roles/cloudasset.viewer` - Asset inventory access
- `roles/recommender.computeViewer` - Compute recommendations
- `roles/recommender.cloudsqlViewer` - Cloud SQL recommendations
- `roles/recommender.cloudAssetInsightsViewer` - Asset insights
- `roles/recommender.billingAccountCudViewer` - Billing CUD recommendations
- `roles/recommender.ucsViewer` - Unattended project recommendations
- `roles/recommender.projectCudViewer` - Project-level CUD recommendations
- `roles/storage.objectCreator` - For storing results (if needed)

#### Additional Recommender Roles
- `roles/recommender.productSuggestionViewer` - Product suggestions
- `roles/recommender.firewallViewer` - Firewall recommendations
- `roles/recommender.errorReportingViewer` - Error Reporting insights
- `roles/recommender.dataflowDiagnosticsViewer` - Dataflow diagnostics
- `roles/recommender.containerDiagnosisViewer` - GKE diagnostics
- `roles/recommender.iamViewer` - IAM recommendations

### Required APIs

The following APIs are automatically enabled by Terraform:
- Cloud Asset API (`cloudasset.googleapis.com`)
- Cloud Build API (`cloudbuild.googleapis.com`)
- Cloud Functions API (`cloudfunctions.googleapis.com`)
- Cloud Scheduler API (`cloudscheduler.googleapis.com`)
- Recommender API (`recommender.googleapis.com`)
- Service Usage API (`serviceusage.googleapis.com`)
- Cloud Resource Manager API (`cloudresourcemanager.googleapis.com`)
- Secret Manager API (`secretmanager.googleapis.com`) - Optional, if using Secret Manager

## Configuration

### Environment Variables

The Cloud Function is configured via environment variables set by Terraform:

#### Required Variables
```bash
GCP_PROJECT                        # GCP project ID where function is deployed
SCAN_SCOPE                         # "organization" or "project" (default: project)
ORGANIZATION_ID                    # Required if SCAN_SCOPE=organization
MIN_COST_THRESHOLD                 # Minimum cost in USD to report (default: 0)
```

#### Slack Notification (choose one method)
```bash
# Method 1: Direct environment variable (default)
USE_SECRET_MANAGER=false
SLACK_HOOK_URL                     # Slack webhook URL

# Method 2: Secret Manager (more secure)
USE_SECRET_MANAGER=true
SLACK_WEBHOOK_SECRET_NAME          # Secret Manager secret name
```

#### Recommender Toggles (all default to true)
```bash
IDLE_VM_RECOMMENDER_ENABLED        # VM idle resource detection
IDLE_DISK_RECOMMENDER_ENABLED      # Disk idle resource detection
IDLE_IMAGE_RECOMMENDER_ENABLED     # Image idle resource detection
IDLE_IP_RECOMMENDER_ENABLED        # IP address idle detection
IDLE_SQL_RECOMMENDER_ENABLED       # Cloud SQL idle detection
RIGHTSIZE_VM_RECOMMENDER_ENABLED   # VM right-sizing recommendations
RIGHTSIZE_SQL_RECOMMENDER_ENABLED  # Cloud SQL right-sizing
MIG_RIGHTSIZE_RECOMMENDER_ENABLED  # MIG machine type optimization
COMMITMENT_USE_RECOMMENDER_ENABLED # CUD usage recommendations
BILLING_USE_RECOMMENDER_ENABLED    # Billing optimization recommendations
```

## Deployment

### Quick Start

1. **Clone the repository**:
```bash
git clone https://github.com/yourusername/FinOps-Guardian.git
cd FinOps-Guardian/gcp-finops
```

2. **Configure your deployment** by creating `terraform.tfvars`:

**For Project-Level Scanning** (recommended for single projects):
```hcl
gcp_project        = "your-project-id"
gcp_region         = "us-central1"
recommender_bucket = "your-project-recommender"
scan_scope         = "project"
slack_webhook_url  = "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
job_schedule       = "0 0 * * *"  # Daily at midnight
job_timezone       = "America/New_York"

# All recommenders enabled by default (set to false to disable)
idle_vm_recommender_enabled        = true
idle_disk_recommender_enabled      = true
# ... etc
```

**For Organization-Level Scanning** (for multi-project organizations):
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

3. **Configure Terraform backend** (edit `backend.tf`):
```hcl
terraform {
  backend "gcs" {
    bucket = "your-terraform-state-bucket"
    prefix = "recommender/org-checker"
  }
}
```

4. **Deploy with Terraform**:
```bash
# Create backend bucket
gsutil mb -p your-project-id -l us-central1 gs://your-terraform-state-bucket

# Initialize and deploy
terraform init
terraform plan
terraform apply
```

### Deployed Resources

Terraform creates the following resources:
1. **Service Account** with appropriate IAM roles (org or project level)
2. **Cloud Storage bucket** for function source code
3. **Cloud Function** (Python 3.12) for recommendation checking
4. **Pub/Sub topic** for function triggering
5. **Cloud Scheduler** job for automated execution
6. **Secret Manager** resources (if `use_secret_manager = true`)
7. **API enablement** for all required services

## Notifications

Recommendations are sent to Slack with the following information:
- GCP Project ID
- Recommendation type
- Recommended action
- Description
- Potential cost impact
- Currency
- Duration of the projection

## Development

### Code Structure

```
scripts/cloudfunctions/recommender-checker/
├── main.py                    # Cloud Function entry point
├── requirements.txt           # Python dependencies
└── localpackage/
    └── recommender/
        ├── __init__.py
        ├── factory.py         # Factory pattern for dynamic loading
        ├── models.py          # Data models (ProjectInfo, CostImpact)
        ├── recommender.py     # Base Recommender class
        ├── compute/
        │   ├── idle_resource.py      # VM, Disk, Image, IP idle detection
        │   ├── rightsize_resource.py # VM right-sizing
        │   ├── mig_rightsize.py      # MIG machine type optimization
        │   ├── comm_use.py           # Commitment usage
        │   └── billing_use.py        # Billing optimization
        └── cloudsql/
            ├── idle_resource.py      # Cloud SQL idle detection
            └── rightsize_resource.py # Cloud SQL right-sizing
```

### Key Design Patterns

1. **Factory Pattern**: `factory.py` dynamically loads recommenders based on environment variables
2. **Inheritance**: All recommenders extend base `Recommender` class with common `detect()` logic
3. **Data Models**: Type-safe data classes in `models.py` for structured data
4. **Dependency Injection**: Recommenders set their own IDs internally

### Adding New Recommenders

To add a new recommender:

1. **Create a new recommender class**:
```python
# localpackage/recommender/your_category/your_recommender.py
from ..recommender import Recommender

class YourRecommender(Recommender):
    def __init__(self):
        recommender_id = "google.service.YourRecommenderType"
        asset_type = "service.googleapis.com/ResourceType"
        super().__init__(recommender_id, asset_type)
```

2. **Register in factory** (`factory.py`):
```python
from .your_category.your_recommender import YourRecommender

_RECOMMENDERS: Dict[str, Type[Recommender]] = {
    # ... existing recommenders
    "YOUR_RECOMMENDER": YourRecommender,
}
```

3. **Add Terraform variable** (`variables.tf`):
```hcl
variable "your_recommender_enabled" {
  type        = bool
  default     = true
  description = "Enable Your Recommender"
}
```

4. **Add to Cloud Function environment** (`main.tf`):
```hcl
environment_variables = merge(
  {
    # ... existing vars
    YOUR_RECOMMENDER_ENABLED = var.your_recommender_enabled
  },
  # ...
)
```

### Testing

The project includes comprehensive test coverage (92%):

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Run with coverage
pytest --cov=localpackage --cov-report=html

# Run specific test
pytest tests/test_factory.py -v
```

See `TESTING.md` for detailed testing documentation.

## Terraform Variables

### Required Variables
| Variable | Type | Description |
|----------|------|-------------|
| `gcp_project` | string | GCP project ID where resources will be deployed |
| `gcp_region` | string | Region for resource deployment (e.g., `us-central1`) |
| `recommender_bucket` | string | Name for the Cloud Storage bucket |
| `slack_webhook_url` | string | Webhook URL for Slack notifications |

### Optional Variables
| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `scan_scope` | string | `"project"` | Scan scope: `"organization"` or `"project"` |
| `organization_id` | string | `""` | GCP organization ID (required if `scan_scope="organization"`) |
| `job_schedule` | string | `"0 0 * * *"` | Cron schedule (default: daily at midnight) |
| `job_timezone` | string | `"America/New_York"` | Timezone for scheduler |
| `min_cost_threshold` | number | `0` | Minimum cost in USD to report recommendations |
| `use_secret_manager` | bool | `false` | Use Secret Manager for webhook URL instead of env var |

### Recommender Toggles (all default to `true`)
| Variable | Description |
|----------|-------------|
| `idle_vm_recommender_enabled` | Enable VM idle resource detection |
| `idle_disk_recommender_enabled` | Enable disk idle resource detection |
| `idle_image_recommender_enabled` | Enable image idle resource detection |
| `idle_ip_recommender_enabled` | Enable IP address idle detection |
| `idle_sql_recommender_enabled` | Enable Cloud SQL idle detection |
| `rightsize_vm_recommender_enabled` | Enable VM right-sizing recommendations |
| `rightsize_sql_recommender_enabled` | Enable Cloud SQL right-sizing |
| `mig_rightsize_recommender_enabled` | Enable MIG machine type optimization |
| `commitment_use_recommender_enabled` | Enable CUD usage recommendations |
| `billing_use_recommender_enabled` | Enable billing optimization recommendations |

## Manual Testing

### Trigger Function Manually
```bash
# Trigger via Pub/Sub
gcloud pubsub topics publish organization-checker \
  --project=your-project-id \
  --message='{"test": "manual_trigger"}'

# View logs
gcloud functions logs read org-checker \
  --region=your-region \
  --project=your-project-id \
  --limit=50
```

### Query Cloud Logging
```bash
# View structured logs
gcloud logging read \
  "resource.type=cloud_function AND resource.labels.function_name=org-checker" \
  --project=your-project-id \
  --limit=20 \
  --format=json
```

### Check Scheduled Job
```bash
# View scheduler configuration
gcloud scheduler jobs describe org_checker_scheduler \
  --location=your-region \
  --project=your-project-id

# Manually trigger scheduler
gcloud scheduler jobs run org_checker_scheduler \
  --location=your-region \
  --project=your-project-id
```

## Monitoring and Observability

- **Cloud Logging**: All logs include execution_id, source location, and distributed trace IDs
- **Cloud Monitoring**: Monitor function execution metrics, errors, and latency
- **Slack Notifications**: Receive immediate alerts for cost-saving recommendations
- **Structured Logs**: Filter by severity, recommender type, or execution ID

## Security Best Practices

1. **Secret Management**: Use Secret Manager for sensitive credentials in production
2. **IAM Least Privilege**: Only grant necessary recommender viewer roles
3. **Network Security**: Function runs in Google-managed environment
4. **Audit Logging**: All API calls logged to Cloud Audit Logs
5. **No Hardcoded Credentials**: All secrets via environment variables or Secret Manager

## Troubleshooting

### Function Not Finding Recommendations
- Verify IAM permissions at organization/project level
- Check that resources exist in the scanned scope
- Review `MIN_COST_THRESHOLD` setting (may be filtering out low-cost items)

### Slack Notifications Not Working
- Verify webhook URL is correct
- Test webhook manually with `curl`
- Check function logs for HTTP errors

### Permission Denied Errors
- Ensure service account has all required roles
- For organization scanning, verify organization-level IAM bindings
- For project scanning, verify project-level IAM bindings

## Roadmap

- [ ] Multi-channel notifications (Email, PagerDuty, etc.)
- [ ] Recommendation history tracking in BigQuery
- [ ] Dashboard for visualization (Data Studio/Looker)
- [ ] Automatic remediation workflows
- [ ] Cost trend analysis
- [ ] Custom recommendation filters

## Contributing

Contributions are welcome! Please:

1. **Follow existing patterns**: Use factory pattern for new recommenders
2. **Write tests**: Maintain 80%+ code coverage
3. **Update documentation**: README, TESTING.md, and inline comments
4. **Use structured logging**: Include proper metadata in log messages
5. **Test thoroughly**: Verify in both org and project scopes

## License

See LICENSE file for details.

## Support

For issues and feature requests, please open a GitHub issue.