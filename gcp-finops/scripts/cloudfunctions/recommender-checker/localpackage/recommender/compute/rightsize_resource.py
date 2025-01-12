from ..recommender import Recommender


class VMRightSizeResourceRecommender(Recommender):
    def __init__(self):
        recommender_id = "google.compute.instance.MachineTypeRecommender"
        asset_type = "compute.googleapis.com/Instance"
        super().__init__(recommender_id, asset_type)

    def detect(self) -> None:
        assets_list = self._search_assets()
        for asset in assets_list:
            project_number = asset.project.split("/")[-1]
            project_name = asset.name.split("/projects/")[1].split("/")[0]
            print(
                f"check {project_name} {asset.display_name} GCE instance rightsize recommendation"
            )
            recommendations = self._list_recommendations(
                project_number, asset.location)
            if not recommendations:
                continue
            for recommendation in recommendations:
                payload = self._generate_slack_payload(
                    project_name, recommendation)
                print(payload)
                self._post_slack_message(payload)
