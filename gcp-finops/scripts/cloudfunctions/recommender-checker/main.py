import os
from localpackage.recommender.compute.idle_resource import VMIdleResourceRecommender
from localpackage.recommender.compute.idle_resource import DiskIdleResourceRecommender
from localpackage.recommender.compute.idle_resource import ImageIdleResourceRecommender
from localpackage.recommender.compute.idle_resource import IpIdleResourceRecommender
from localpackage.recommender.compute.rightsize_resource import VMRightSizeResourceRecommender

from localpackage.recommender.compute.comm_use import CommUseRecommender
from localpackage.recommender.compute.billing_use import BillingUseRecommender

from localpackage.recommender.cloudsql.idle_resource import CloudSQLIdleResourceRecommender
from localpackage.recommender.cloudsql.rightsize_resource import CloudSQLRightSizeResourceRecommender


def check_recommender(_event, context):
    print(
        f"This Function was triggered by messageId {context.event_id} published at {context.timestamp}"
    )

    # Cloud SQL recommenders
    if os.environ.get("IDLE_SQL_RECOMMENDER_ENABLED", "false") == "true":
        idle_sql_recommender = CloudSQLIdleResourceRecommender()
        idle_sql_recommender.detect()

    if os.environ.get("RIGHTSIZE_SQL_RECOMMENDER_ENABLED", "false") == "true":
        rightsize_resource = CloudSQLRightSizeResourceRecommender()
        rightsize_resource.detect()

    # GCE recommenders
    if os.environ.get("IDLE_DISK_RECOMMENDER_ENABLED", "false") == "true":
        idle_disk_recommender = DiskIdleResourceRecommender()
        idle_disk_recommender.detect()

    if os.environ.get('IDLE_IMAGE_RECOMMENDER_ENABLED', "false") == 'true':
        idle_image_recommender = ImageIdleResourceRecommender()
        idle_image_recommender.detect()

    if os.environ.get("IDLE_IP_RECOMMENDER_ENABLED", "false") == "true":
        idle_ip_recommender = IpIdleResourceRecommender()
        idle_ip_recommender.detect()

    if os.environ.get("IDLE_VM_RECOMMENDER_ENABLED", "false") == "true":
        idle_vm_recommender = VMIdleResourceRecommender()
        idle_vm_recommender.detect()

    if os.environ.get("RIGHTSIZE_VM_RECOMMENDER_ENABLED", "false") == "true":
        rightsize_resource = VMRightSizeResourceRecommender()
        rightsize_resource.detect()

    if os.environ.get("COMMITMENT_USE_RECOMMENDER_ENABLED", "false") == "true":
        commuserecommender = CommUseRecommender()
        commuserecommender.detect()

    if os.environ.get("BILLING_USE_RECOMMENDER_ENABLED", "false") == "true":
        billinguserecommender = BillingUseRecommender()
        billinguserecommender.detect()
