import json
import logging
import os
from typing import List, Optional, TypedDict
from urllib.request import Request, urlopen

from google.api_core import retry
from google.api_core.exceptions import GoogleAPIError
from google.cloud import asset_v1, logging as cloud_logging
from google.cloud import recommender_v1
from google.cloud import secretmanager
from google.cloud.asset_v1.types.assets import ResourceSearchResult
from google.cloud.recommender_v1.types.recommendation import Recommendation
from proto.marshal.collections.repeated import RepeatedComposite

from .models import CostImpact, ProjectInfo, RecommendationSummary

# Setup Cloud Logging
try:
    client = cloud_logging.Client()
    client.setup_logging()
except Exception:
    # Fallback to standard logging if Cloud Logging is not available
    pass

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


SlackPayload = TypedDict("SlackPayload", {"text": str})

class Recommender:

    def __init__(self, recommender_id: str, asset_type: str, ignore_descriptions: List[str] = None):
        """Initialize the Recommender.

        Args:
            recommender_id: GCP Recommender ID
            asset_type: GCP Asset type to search for
            ignore_descriptions: List of description patterns to ignore
        """
        # AssetTypes: https://cloud.google.com/asset-inventory/docs/supported-asset-types
        # RecommenderId: https://cloud.google.com/recommender/docs/recommenders
        self.recommender_client = recommender_v1.RecommenderClient()
        self.recommender_id = recommender_id
        self.asset_client = asset_v1.AssetServiceClient()
        self.asset_type = asset_type
        self.ignore_descriptions = ignore_descriptions or [""]

        # Support both organization and project level scanning
        self.scan_scope = os.environ.get("SCAN_SCOPE", "organization").lower()
        self.organization_id = os.environ.get("ORGANIZATION_ID", "")
        self.project_id = os.environ.get("GCP_PROJECT", "")
        self.min_cost_threshold = float(os.environ.get("MIN_COST_THRESHOLD", "0"))

        logger.info(
            f"Initialized {self.__class__.__name__}",
            extra={
                "recommender_id": recommender_id,
                "asset_type": asset_type,
                "scan_scope": self.scan_scope,
                "project_id": self.project_id if self.scan_scope == "project" else None,
                "organization_id": self.organization_id if self.scan_scope == "organization" else None
            }
        )

    @retry.Retry(predicate=retry.if_transient_error, deadline=120.0)
    def _search_assets(self) -> List[ResourceSearchResult]:
        """Search for assets in the organization or project with retry logic.

        Returns:
            List of ResourceSearchResult objects

        Raises:
            GoogleAPIError: If API call fails after retries
        """
        asset_list = []
        page_token = ""

        # Determine scope based on configuration
        if self.scan_scope == "project":
            scope = f"projects/{self.project_id}"
        else:
            scope = f"organizations/{self.organization_id}"

        try:
            while True:
                response = self.asset_client.search_all_resources(
                    request={
                        "scope": scope,
                        "asset_types": [self.asset_type],
                        "page_token": page_token,
                    }
                )
                asset_list += response.results
                page_token = response.next_page_token
                if not page_token:
                    break

            logger.info(
                f"Found {len(asset_list)} assets",
                extra={
                    "asset_type": self.asset_type,
                    "asset_count": len(asset_list),
                    "scan_scope": self.scan_scope,
                    "scope": scope
                }
            )
            return asset_list
        except GoogleAPIError as e:
            logger.error(
                f"Error searching assets: {e}",
                extra={
                    "asset_type": self.asset_type,
                    "scan_scope": self.scan_scope,
                    "scope": scope
                },
                exc_info=True
            )
            raise

    @retry.Retry(predicate=retry.if_transient_error, deadline=60.0)
    def _list_recommendations(
        self, project_number: str, zone: str
    ) -> RepeatedComposite:
        """List recommendations for a project/zone with retry logic.

        Args:
            project_number: GCP project number
            zone: GCP zone/location

        Returns:
            RepeatedComposite of recommendations

        Raises:
            GoogleAPIError: If API call fails after retries
        """
        try:
            response = self.recommender_client.list_recommendations(
                request={
                    "parent": f"projects/{project_number}/locations/{zone}/recommenders/{self.recommender_id}"
                }
            )
            return response.recommendations
        except GoogleAPIError as e:
            logger.warning(
                f"Error listing recommendations: {e}",
                extra={
                    "project_number": project_number,
                    "zone": zone,
                    "recommender_id": self.recommender_id
                }
            )
            # Return empty list instead of raising to continue processing other projects
            return []

    def _extract_project_info(self, asset: ResourceSearchResult) -> ProjectInfo:
        """Extract project information from asset.

        Args:
            asset: ResourceSearchResult object

        Returns:
            ProjectInfo dataclass with project details
        """
        project_number = asset.project.split("/")[-1]
        project_name = asset.name.split("/projects/")[1].split("/")[0]
        return ProjectInfo(number=project_number, name=project_name)

    def _calculate_cost_impact(self, recommendation: Recommendation) -> CostImpact:
        """Calculate cost impact from recommendation.

        Args:
            recommendation: Recommendation object

        Returns:
            CostImpact dataclass with cost details
        """
        duration = recommendation.primary_impact.cost_projection.duration
        duration_str = str(duration).split(",")[0] if duration else "0"
        units = recommendation.primary_impact.cost_projection.cost.units
        nanos = recommendation.primary_impact.cost_projection.cost.nanos
        cost = nanos * (-10**-9)
        total_cost = abs(units) + round(cost, 2) if cost else 0

        return CostImpact(
            units=units,
            nanos=nanos,
            currency=recommendation.primary_impact.cost_projection.cost.currency_code,
            duration=duration_str,
            total_cost=total_cost
        )
    def _generate_slack_payload(
        self, project: str, recommendation: Recommendation
    ) -> SlackPayload:
        """Generate Slack notification payload.

        Args:
            project: Project ID
            recommendation: Recommendation object

        Returns:
            SlackPayload dictionary
        """
        _id = self.recommender_id.strip("google.")
        cost_impact = self._calculate_cost_impact(recommendation)

        message = (
            f"[GCP PROJECT ID] {project} Recommender - ({_id})\n"
            f"```"
            f"Recommended Action: {recommendation.recommender_subtype}\n"
            f"Description: {recommendation.description}\n"
            f"Cost Savings: {cost_impact.total_cost}\n"
            f"Currency: {cost_impact.currency}\n"
            f"Duration: {cost_impact.duration}\n"
            f"```"
        )
        logger.info(
            "Generated recommendation",
            extra={
                "project": project,
                "recommender_type": _id,
                "cost_savings": cost_impact.total_cost,
                "currency": cost_impact.currency
            }
        )
        payload: SlackPayload = {"text": message}
        return payload

    def _get_slack_webhook_url(self) -> Optional[str]:
        """Get Slack webhook URL from environment or Secret Manager.

        Returns:
            Slack webhook URL or None
        """
        # Try Secret Manager first
        use_secret_manager = os.environ.get("USE_SECRET_MANAGER", "false").lower() == "true"
        if use_secret_manager:
            try:
                secret_name = os.environ.get("SLACK_WEBHOOK_SECRET_NAME")
                if secret_name:
                    client = secretmanager.SecretManagerServiceClient()
                    response = client.access_secret_version(name=secret_name)
                    webhook_url = response.payload.data.decode("UTF-8")
                    logger.info("Retrieved Slack webhook from Secret Manager")
                    return webhook_url
            except Exception as e:
                logger.warning(f"Failed to retrieve secret from Secret Manager: {e}")

        # Fallback to environment variable
        return os.environ.get("SLACK_HOOK_URL")

    def _post_slack_message(self, payload: SlackPayload) -> None:
        """Post message to Slack.

        Args:
            payload: SlackPayload dictionary
        """
        slack_hook_url = self._get_slack_webhook_url()
        if slack_hook_url is None:
            logger.info("No Slack webhook configured, skipping notification")
            return

        try:
            req = Request(slack_hook_url, json.dumps(payload).encode("UTF-8"))
            with urlopen(req) as response:
                response.read()
                logger.info("Message posted to Slack successfully")
        except Exception as e:
            logger.error(
                f"Failed to post message to Slack: {e}",
                extra={"payload": payload},
                exc_info=True
            )

    def _process_recommendations(
        self, project_name: str, recommendations: RepeatedComposite
    ) -> None:
        """Process recommendations and send notifications.

        Args:
            project_name: Project ID
            recommendations: List of recommendations
        """
        if not recommendations:
            return

        processed_count = 0
        for recommendation in recommendations:
            # Calculate cost impact
            cost_impact = self._calculate_cost_impact(recommendation)

            # Skip if below threshold (per user's CLAUDE.md: never include <2% savings)
            if cost_impact.total_cost < self.min_cost_threshold:
                logger.debug(
                    f"Skipping recommendation below cost threshold",
                    extra={
                        "project": project_name,
                        "cost": cost_impact.total_cost,
                        "threshold": self.min_cost_threshold
                    }
                )
                continue

            # Generate and send notification
            payload = self._generate_slack_payload(project_name, recommendation)
            self._post_slack_message(payload)
            processed_count += 1

        logger.info(
            f"Processed {processed_count} recommendations for project {project_name}",
            extra={
                "project": project_name,
                "total_recommendations": len(recommendations),
                "processed": processed_count
            }
        )

    def detect(self) -> None:
        """Main detection method - searches assets and processes recommendations.

        This is the default implementation that can be overridden by subclasses
        if custom behavior is needed.
        """
        try:
            logger.info(
                f"Starting recommendation detection",
                extra={"recommender_id": self.recommender_id}
            )

            assets_list = self._search_assets()

            total_recommendations = 0
            for asset in assets_list:
                project_info = self._extract_project_info(asset)

                recommendations = self._list_recommendations(
                    project_info.number, asset.location
                )

                if recommendations:
                    total_recommendations += len(recommendations)
                    self._process_recommendations(project_info.name, recommendations)

            logger.info(
                f"Completed recommendation detection",
                extra={
                    "recommender_id": self.recommender_id,
                    "total_assets": len(assets_list),
                    "total_recommendations": total_recommendations
                }
            )
        except Exception as e:
            logger.error(
                f"Error in detect() method: {e}",
                extra={"recommender_id": self.recommender_id},
                exc_info=True
            )
            raise
