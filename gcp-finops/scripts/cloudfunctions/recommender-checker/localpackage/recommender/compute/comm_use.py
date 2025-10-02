"""Compute commitment usage recommenders."""

from ..recommender import Recommender


class CommUseRecommender(Recommender):
    """Recommender for committed use discounts."""

    def __init__(self):
        recommender_id = "google.compute.commitment.UsageCommitmentRecommender"
        asset_type = "compute.googleapis.com/Commitment"
        super().__init__(recommender_id, asset_type)
