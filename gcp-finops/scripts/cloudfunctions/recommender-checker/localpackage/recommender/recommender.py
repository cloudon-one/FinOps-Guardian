import json
import os
from typing import List, TypedDict
from urllib.request import Request, urlopen

from google.cloud import asset_v1
from google.cloud import recommender_v1
from google.cloud.asset_v1.types.assets import ResourceSearchResult
from google.cloud.recommender_v1.types.recommendation import Recommendation
from proto.marshal.collections.repeated import RepeatedComposite


class Recommender:
    SlackPayload = TypedDict("SlackPayload", {"text": str})

    def __init__(self, recommender_id, asset_type, ignore_descriptions=[""]):
        # AssetTypes: https://cloud.google.com/asset-inventory/docs/supported-asset-types
        # RecommenderId: https://cloud.google.com/recommender/docs/recommenders
        self.recommender_client = recommender_v1.RecommenderClient()
        self.recommender_id = recommender_id
        self.asset_client = asset_v1.AssetServiceClient()
        self.asset_type = asset_type
        self.ignore_descriptions = ignore_descriptions

    def _search_assets(self) -> List[ResourceSearchResult]:
        asset_list = []
        page_token = ""
        while True:
            response = self.asset_client.search_all_resources(
                request={
                    "scope": f"organizations/{os.environ['ORGANIZATION_ID']}",
                    "asset_types": [self.asset_type],
                    "page_token": page_token,
                }
            )
            asset_list += response.results
            page_token = response.next_page_token
            if not page_token:
                break
        return asset_list

    def _list_recommendations(
        self, project_number: str, zone: str
    ) -> RepeatedComposite:
        response = self.recommender_client.list_recommendations(
            request={
                "parent": f"projects/{project_number}/locations/{zone}/recommenders/{self.recommender_id}"
            }
        )
        return response.recommendations

    # send notification to slack
    def _generate_slack_payload(
        self, project: str, recommendation: Recommendation
    ) -> SlackPayload:
        _id = self.recommender_id.strip("google.")
        duration = recommendation.primary_impact.cost_projection.duration
        duration = str(duration).split(",")[0] if duration else 0
        units = recommendation.primary_impact.cost_projection.cost.units
        cost = recommendation.primary_impact.cost_projection.cost.nanos * \
            (-10**-9)
        cost = abs(units)+round(cost, 2) if cost else 0
        message = (
            f"[GCP PROJECT ID] {project} Recommender - ({_id})\n"
            f"```"
            f"Recommended Action: {recommendation.recommender_subtype}\n"
            f"Description: {recommendation.description}\n"
            f"Cost: {cost}\n"
            f"Currency: {recommendation.primary_impact.cost_projection.cost.currency_code}\n"
            f"Duration: {duration}\n"
            f"```"
        )
        print(message)
        payload = {"text": message}
        return payload

    def _post_slack_message(self, payload: SlackPayload) -> None:
        slack_hook_url = os.environ.get("SLACK_HOOK_URL")
        if slack_hook_url is None:
            print(payload)
            return
        req = Request(slack_hook_url, json.dumps(payload).encode("UTF-8"))
        with urlopen(req) as response:
            response.read()
            print("Message posted to Slack")
