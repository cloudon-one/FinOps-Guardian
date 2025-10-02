"""Compute idle resource recommenders."""

from ..recommender import Recommender


class VMIdleResourceRecommender(Recommender):
    """Recommender for idle VM instances."""

    def __init__(self):
        recommender_id = "google.compute.instance.IdleResourceRecommender"
        asset_type = "compute.googleapis.com/Instance"
        super().__init__(recommender_id, asset_type)


class DiskIdleResourceRecommender(Recommender):
    """Recommender for idle persistent disks."""

    def __init__(self):
        recommender_id = "google.compute.disk.IdleResourceRecommender"
        asset_type = "compute.googleapis.com/Disk"
        super().__init__(recommender_id, asset_type)


class ImageIdleResourceRecommender(Recommender):
    """Recommender for idle custom images."""

    def __init__(self):
        recommender_id = "google.compute.image.IdleResourceRecommender"
        asset_type = "compute.googleapis.com/Image"
        super().__init__(recommender_id, asset_type)


class IpIdleResourceRecommender(Recommender):
    """Recommender for idle IP addresses."""

    def __init__(self):
        recommender_id = "google.compute.address.IdleResourceRecommender"
        asset_type = "compute.googleapis.com/Address"
        super().__init__(recommender_id, asset_type)
