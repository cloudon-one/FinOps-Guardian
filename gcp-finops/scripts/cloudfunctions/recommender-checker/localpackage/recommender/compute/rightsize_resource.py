"""Compute right-sizing recommenders."""

from ..recommender import Recommender


class VMRightSizeResourceRecommender(Recommender):
    """Recommender for VM machine type right-sizing."""

    def __init__(self):
        recommender_id = "google.compute.instance.MachineTypeRecommender"
        asset_type = "compute.googleapis.com/Instance"
        super().__init__(recommender_id, asset_type)
