from ..recommender import Recommender


class CloudSQLIdleResourceRecommender(Recommender):
    def __init__(self):
        recommender_id = 'google.cloudsql.instance.IdleRecommender'
        asset_type = 'sqladmin.googleapis.com/Instance'
        super().__init__(recommender_id, asset_type)

    def detect(self) -> None:
        assets_list = self._search_assets()
        for asset in assets_list:
            project_number = asset.project.split('/')[-1]
            project_name = asset.name.split('/projects/')[1].split('/')[0]
            print(f'check {project_name} {asset.display_name} cloudsql instance idle recommendation')
            recommendations = self._list_recommendations(project_number, asset.location)
            if not recommendations:
                continue
            for recommendation in recommendations:
                payload = self._generate_slack_payload(project_name, recommendation)
                print(payload)
                self._post_slack_message(payload)
