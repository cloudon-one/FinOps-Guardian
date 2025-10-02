"""Cloud SQL right-sizing recommenders."""

from ..recommender import Recommender


class CloudSQLRightSizeResourceRecommender(Recommender):
    """Recommender for Cloud SQL instance right-sizing."""

    def __init__(self):
        recommender_id = "google.cloudsql.instance.OverprovisionedRecommender"
        asset_type = "sqladmin.googleapis.com/Instance"
        super().__init__(recommender_id, asset_type)
