"""Managed Instance Group right-sizing recommenders."""

from ..recommender import Recommender


class MIGMachineTypeRecommender(Recommender):
    """Recommender for Managed Instance Group machine type right-sizing.

    This recommender was added to GCP after 2022 and provides recommendations
    for optimizing the machine types used in Managed Instance Groups (MIGs).
    """

    def __init__(self):
        recommender_id = "google.compute.instanceGroupManager.MachineTypeRecommender"
        asset_type = "compute.googleapis.com/InstanceGroupManager"
        super().__init__(recommender_id, asset_type)
