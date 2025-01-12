from ..recommender import Recommender

# Idle VMs


class VMIdleResourceRecommender(Recommender):
    def __init__(self):
        recommender_id = "google.compute.instance.IdleResourceRecommender"
        asset_type = "compute.googleapis.com/Instance"
        super().__init__(recommender_id, asset_type)

    def detect(self) -> None:
        assets_list = self._search_assets()
        for asset in assets_list:
            project_number = asset.project.split("/")[-1]
            project_name = asset.name.split("/projects/")[1].split("/")[0]
            # print(
            #     f'check {project_name} {asset.display_name} GCE resources recommendation')
            recommendations = self._list_recommendations(
                project_number, asset.location)
            if not recommendations:
                continue
            for recommendation in recommendations:
                payload = self._generate_slack_payload(
                    project_name, recommendation)
                self._post_slack_message(payload)


# Idle Disks


class DiskIdleResourceRecommender(Recommender):
    def __init__(self):
        recommender_id = "google.compute.disk.IdleResourceRecommender"
        asset_type = "compute.googleapis.com/Disk"
        super().__init__(recommender_id, asset_type)

    def detect(self) -> None:
        assets_list = self._search_assets()
        for asset in assets_list:
            project_number = asset.project.split("/")[-1]
            project_name = asset.name.split("/projects/")[1].split("/")[0]
            # print(
            #     f'check {project_name} {asset.display_name} GCE resources recommendation')
            recommendations = self._list_recommendations(
                project_number, asset.location)
            if not recommendations:
                continue
            for recommendation in recommendations:
                payload = self._generate_slack_payload(
                    project_name, recommendation)
                self._post_slack_message(payload)


# Idle Images


class ImageIdleResourceRecommender(Recommender):
    def __init__(self):
        recommender_id = "google.compute.image.IdleResourceRecommender"
        asset_type = "compute.googleapis.com/Image"
        super().__init__(recommender_id, asset_type)

    def detect(self) -> None:
        assets_list = self._search_assets()
        for asset in assets_list:
            project_number = asset.project.split("/")[-1]
            project_name = asset.name.split("/projects/")[1].split("/")[0]
            # print(
            #     f'check {project_name} {asset.display_name} GCE resources recommendation')
            recommendations = self._list_recommendations(
                project_number, asset.location)
            if not recommendations:
                continue
            for recommendation in recommendations:
                payload = self._generate_slack_payload(
                    project_name, recommendation)
                self._post_slack_message(payload)


# Idle IPs


class IpIdleResourceRecommender(Recommender):
    def __init__(self):
        recommender_id = "google.compute.address.IdleResourceRecommender"
        asset_type = "compute.googleapis.com/Address"
        super().__init__(recommender_id, asset_type)

    def detect(self) -> None:
        assets_list = self._search_assets()
        for asset in assets_list:
            project_number = asset.project.split("/")[-1]
            project_name = asset.name.split("/projects/")[1].split("/")[0]
            # print(
            #     f'check {project_name} {asset.display_name} GCE resources recommendation')
            recommendations = self._list_recommendations(
                project_number, asset.location)
            if not recommendations:
                continue
            for recommendation in recommendations:
                payload = self._generate_slack_payload(
                    project_name, recommendation)
                self._post_slack_message(payload)
