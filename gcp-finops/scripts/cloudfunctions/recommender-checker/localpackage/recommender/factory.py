"""Factory pattern for creating recommender instances."""

import logging
import os
from typing import Dict, List, Type

from .recommender import Recommender
from .compute.idle_resource import (
    VMIdleResourceRecommender,
    DiskIdleResourceRecommender,
    ImageIdleResourceRecommender,
    IpIdleResourceRecommender
)
from .compute.rightsize_resource import VMRightSizeResourceRecommender
from .compute.mig_rightsize import MIGMachineTypeRecommender
from .compute.comm_use import CommUseRecommender
from .compute.billing_use import BillingUseRecommender
from .cloudsql.idle_resource import CloudSQLIdleResourceRecommender
from .cloudsql.rightsize_resource import CloudSQLRightSizeResourceRecommender

logger = logging.getLogger(__name__)


class RecommenderFactory:
    """Factory for creating and managing recommender instances."""

    # Registry of available recommenders
    _RECOMMENDERS: Dict[str, Type[Recommender]] = {
        "IDLE_VM_RECOMMENDER": VMIdleResourceRecommender,
        "IDLE_DISK_RECOMMENDER": DiskIdleResourceRecommender,
        "IDLE_IMAGE_RECOMMENDER": ImageIdleResourceRecommender,
        "IDLE_IP_RECOMMENDER": IpIdleResourceRecommender,
        "IDLE_SQL_RECOMMENDER": CloudSQLIdleResourceRecommender,
        "RIGHTSIZE_VM_RECOMMENDER": VMRightSizeResourceRecommender,
        "RIGHTSIZE_SQL_RECOMMENDER": CloudSQLRightSizeResourceRecommender,
        "MIG_RIGHTSIZE_RECOMMENDER": MIGMachineTypeRecommender,
        "COMMITMENT_USE_RECOMMENDER": CommUseRecommender,
        "BILLING_USE_RECOMMENDER": BillingUseRecommender,
    }

    @classmethod
    def get_enabled_recommenders(cls) -> List[Recommender]:
        """Get all enabled recommenders based on environment variables.

        Returns:
            List of instantiated Recommender objects

        Example environment variables:
            IDLE_VM_RECOMMENDER_ENABLED=true
            IDLE_SQL_RECOMMENDER_ENABLED=false
        """
        enabled_recommenders = []

        for key, recommender_class in cls._RECOMMENDERS.items():
            env_var = f"{key}_ENABLED"
            is_enabled = os.environ.get(env_var, "false").lower() == "true"

            if is_enabled:
                try:
                    # Instantiate recommender with required parameters
                    recommender = recommender_class(recommender_id=key)
                    enabled_recommenders.append(recommender)
                    logger.info(
                        f"Enabled recommender: {recommender_class.__name__}",
                        extra={"recommender": recommender_class.__name__}
                    )
                except Exception as e:
                    logger.error(
                        f"Failed to instantiate {recommender_class.__name__}: {e}",
                        extra={"recommender": recommender_class.__name__},
                        exc_info=True
                    )
            else:
                logger.debug(
                    f"Skipping disabled recommender: {recommender_class.__name__}",
                    extra={"recommender": recommender_class.__name__}
                )

        logger.info(
            f"Total enabled recommenders: {len(enabled_recommenders)}",
            extra={"count": len(enabled_recommenders)}
        )

        return enabled_recommenders

    @classmethod
    def register_recommender(cls, key: str, recommender_class: Type[Recommender]) -> None:
        """Register a new recommender type.

        Args:
            key: Environment variable prefix (e.g., "CUSTOM_RECOMMENDER")
            recommender_class: Recommender class to register
        """
        cls._RECOMMENDERS[key] = recommender_class
        logger.info(f"Registered new recommender: {key} -> {recommender_class.__name__}")

    @classmethod
    def list_available_recommenders(cls) -> List[str]:
        """List all available recommender types.

        Returns:
            List of recommender keys
        """
        return list(cls._RECOMMENDERS.keys())
