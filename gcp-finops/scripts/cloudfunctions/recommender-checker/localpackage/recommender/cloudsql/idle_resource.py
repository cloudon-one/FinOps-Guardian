"""Cloud SQL idle resource recommenders."""

from ..recommender import Recommender


class CloudSQLIdleResourceRecommender(Recommender):
    """Recommender for idle Cloud SQL instances."""

    def __init__(self):
        recommender_id = "google.cloudsql.instance.IdleRecommender"
        asset_type = "sqladmin.googleapis.com/Instance"
        super().__init__(recommender_id, asset_type)
