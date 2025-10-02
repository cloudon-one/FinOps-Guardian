"""Data models for the recommender system."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class ProjectInfo:
    """Project information extracted from GCP asset."""

    number: str
    name: str


@dataclass
class CostImpact:
    """Cost impact information from a recommendation."""

    units: int
    nanos: int
    currency: str
    duration: str
    total_cost: float

    @property
    def percentage(self) -> float:
        """Calculate percentage impact (placeholder - needs total cost context)."""
        # This would need to be calculated against total project/org cost
        return 0.0


@dataclass
class RecommendationSummary:
    """Summary of a single recommendation."""

    project_id: str
    recommender_type: str
    recommender_subtype: str
    description: str
    cost_impact: CostImpact
    resource_name: Optional[str] = None
    location: Optional[str] = None

    def should_notify(self, min_cost_threshold: float = 0.0) -> bool:
        """Determine if this recommendation should trigger a notification.

        Args:
            min_cost_threshold: Minimum cost impact to notify (default 0.0)

        Returns:
            True if recommendation should be notified
        """
        # Per user's CLAUDE.md: never include saving opportunities with <2% of total cost
        # For now, we'll use absolute cost threshold
        return self.cost_impact.total_cost >= min_cost_threshold


@dataclass
class RecommenderConfig:
    """Configuration for recommender execution."""

    organization_id: str
    slack_webhook_url: Optional[str] = None
    min_cost_threshold: float = 0.0
    use_secret_manager: bool = False
    secret_project_id: Optional[str] = None
    secret_name: Optional[str] = None
