# GCP Organization Recommender

A serverless solution to monitor and receive GCP recommendations across your organization. This system leverages Google Cloud's Recommender API to detect potential cost savings and optimization opportunities.

## Overview

This system runs as a Cloud Function that periodically checks for various types of recommendations across your GCP organization and sends notifications to Slack. It covers multiple resource types including:

- Virtual Machines (GCE)
- Cloud SQL instances
- Disks
- Images
- IP addresses
- Commitment usage
- Billing optimizations

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
   - Organization-level permissions for comprehensive access

2. **Cloud Function**:
   - Runtime: Python 3.9
   - Memory: 512MB
   - Timeout: 300 seconds
   - Triggered by Pub/Sub messages

3. **Storage**:
   - Location: EU
   - Uniform bucket level access enabled
   - Used for function code storage

4. **Cloud Scheduler**:
   - Configurable schedule
   - Retries configured with exponential backoff
   - Publishes to Pub/Sub topic

## Supported Recommenders

The system supports the following recommendation types:

- `google.compute.instance.IdleResourceRecommender` - Identifies idle VM instances
- `google.compute.image.IdleResourceRecommender` - Identifies idle GCE custom images
- `google.compute.address.IdleResourceRecommender` - Identifies idle IP addresses
- `google.compute.disk.IdleResourceRecommender` - Identifies idle GCE disks
- `google.cloudsql.instance.IdleRecommender` - Identifies idle SQL instances
- `google.cloudsql.instance.OverprovisionedRecommender` - Identifies oversized SQL instances
- `google.compute.instance.MachineTypeRecommender` - Identifies opportunities for VM right-sizing
- `google.cloudbilling.commitment.SpendBasedCommitmentRecommender` - Provides spend-based cost savings recommendations
- `google.compute.commitment.UsageCommitmentRecommender` - Provides usage-based cost savings recommendations

## Features

The system can check for multiple types of recommendations:

- **Idle Resources**:
  - VM instances
  - Cloud SQL instances
  - Disks
  - Images
  - IP addresses

- **Right-sizing**:
  - VM instances
  - Cloud SQL instances

- **Cost Optimization**:
  - Commitment usage recommendations
  - Billing usage optimization

## Prerequisites

### Required Deployment Permissions

The user/service account deploying this solution requires:
- `roles/resourcemanager.organizationAdmin` - Organization Admin permission is required for Terraform execution

### Required Service Account Permissions

#### Mandatory Roles
The following roles are required for the service account to collect recommendations at the organization level:
- `roles/cloudasset.viewer`
- `roles/recommender.computeViewer`
- `roles/recommender.cloudsqlViewer`
- `roles/recommender.cloudAssetInsightsViewer`
- `roles/recommender.billingAccountCudViewer`
- `roles/recommender.ucsViewer`
- `roles/recommender.projectCudViewer`

#### Optional Roles
Additional roles that may be needed depending on your use case:
- `roles/recommender.productSuggestionViewer`
- `roles/recommender.firewallViewer`
- `roles/recommender.errorReportingViewer`
- `roles/recommender.dataflowDiagnosticsViewer`
- `roles/recommender.containerDiagnosisViewer`
- `roles/recommender.iamViewer`

### Required APIs

The following APIs must be enabled in your project:
- Cloud Asset API
- Cloud Build API
- Cloud Functions API
- Cloud Scheduler API
- Recommender API
- Service Usage API
- Cloud Resource Manager API

## Configuration

### Environment Variables

The following environment variables control the system's behavior:

```
ORGANIZATION_ID                    - Your GCP organization ID
SLACK_HOOK_URL                    - Webhook URL for Slack notifications
IDLE_VM_RECOMMENDER_ENABLED       - Enable/disable VM idle checks
IDLE_SQL_RECOMMENDER_ENABLED      - Enable/disable SQL idle checks
IDLE_DISK_RECOMMENDER_ENABLED     - Enable/disable disk idle checks
IDLE_IMAGE_RECOMMENDER_ENABLED    - Enable/disable image idle checks
IDLE_IP_RECOMMENDER_ENABLED       - Enable/disable IP idle checks
RIGHTSIZE_VM_RECOMMENDER_ENABLED  - Enable/disable VM right-sizing checks
RIGHTSIZE_SQL_RECOMMENDER_ENABLED - Enable/disable SQL right-sizing checks
COMMITMENT_USE_RECOMMENDER_ENABLED- Enable/disable commitment usage checks
BILLING_USE_RECOMMENDER_ENABLED   - Enable/disable billing optimization checks
```

### Service Account Permissions

The service account requires the following roles:
```
roles/cloudasset.viewer
roles/recommender.computeViewer
roles/recommender.cloudsqlViewer
roles/recommender.iamViewer
roles/storage.objectCreator
roles/recommender.cloudAssetInsightsViewer
roles/recommender.billingAccountCudViewer
roles/recommender.ucsViewer
roles/recommender.projectCudViewer
roles/recommender.productSuggestionViewer
roles/recommender.firewallViewer
roles/recommender.errorReportingViewer
roles/recommender.dataflowDiagnosticsViewer
roles/recommender.containerDiagnosisViewer
```

## Deployment

The system is deployed using Terraform. Key deployment resources:

1. Service Account and IAM roles
2. Cloud Storage bucket
3. Cloud Function
4. Pub/Sub topic
5. Cloud Scheduler job

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

- `main.py`: Contains the Cloud Function entry point and recommender initialization
- `recommender.py`: Base class for recommendation handling and Slack notifications
- Individual recommender classes for each resource type

### Adding New Recommenders

To add a new recommender:
1. Create a new class extending the base `Recommender` class
2. Add appropriate environment variable in Terraform
3. Add the initialization in `main.py`

## Terraform Variables

Required variables:
- `gcp_project`: The project ID where resources will be deployed
- `gcp_region`: Region for resource deployment
- `organization_id`: Your GCP organization ID
- `slack_webhook_url`: Webhook URL for Slack notifications
- `job_schedule`: Cloud Scheduler cron schedule
- `job_timezone`: Timezone for the scheduler
- `recommender_bucket`: Name for the Cloud Storage bucket

## Service Account Authorization

To authorize the service account for a client GCP Organization:

```bash
# Set environment variables
export CLIENT_ORG_ID="your-org-id"
export PROJECT_ID="your-project-id"  # authorized service account project

# Add required roles for recommender SA
gcloud organizations add-iam-policy-binding $CLIENT_ORG_ID \
  --member="serviceAccount:organization-checker@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/recommender.cloudAssetInsightsViewer" \
  --role="roles/recommender.computeViewer" \
  --role="roles/recommender.cloudsqlViewer" \
  --role="roles/recommender.billingAccountCudViewer" \
  --role="roles/recommender.ucsViewer" \
  --role="roles/recommender.projectCudViewer"
```

## Work in Progress Features

The following features are currently under development:
- Datastore collections to store recommendations - Simple NoSQL Document DB to collect and store recommendations
- Resources filters per org_id, folder_id, project_id - Pre-defined search queries to filter recommendations

## Contributing

When contributing to this project:
1. Ensure all new recommenders follow the existing pattern
2. Update documentation for any new features
3. Test thoroughly before submitting changes