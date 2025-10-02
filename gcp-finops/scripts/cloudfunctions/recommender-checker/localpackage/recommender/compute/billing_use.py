"""Billing commitment recommenders."""

from ..recommender import Recommender


class BillingUseRecommender(Recommender):
    """Recommender for spend-based commitment discounts."""

    def __init__(self):
        recommender_id = "google.cloudbilling.commitment.SpendBasedCommitmentRecommender"
        asset_type = "compute.googleapis.com/Commitment"
        super().__init__(recommender_id, asset_type)
