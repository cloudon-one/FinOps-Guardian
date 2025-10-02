"""Cloud Function entry point for GCP Organization Recommender.

This function is triggered by Pub/Sub messages and runs enabled recommenders
to detect cost optimization opportunities across the GCP organization.
"""

import logging
from typing import Any

from google.cloud import logging as cloud_logging
from localpackage.recommender.factory import RecommenderFactory

# Setup Cloud Logging
try:
    client = cloud_logging.Client()
    client.setup_logging()
except Exception:
    # Fallback to standard logging if Cloud Logging is not available
    pass

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def check_recommender(_event: Any, context: Any) -> None:
    """Main Cloud Function entry point.

    Args:
        _event: Event payload (not used)
        context: Event context with metadata

    Raises:
        Exception: If critical error occurs during execution
    """
    logger.info(
        "Cloud Function triggered",
        extra={
            "event_id": context.event_id,
            "timestamp": context.timestamp
        }
    )

    try:
        # Get all enabled recommenders using factory pattern
        recommenders = RecommenderFactory.get_enabled_recommenders()

        if not recommenders:
            logger.warning("No recommenders enabled - check environment variables")
            return

        # Execute all enabled recommenders
        total_success = 0
        total_failed = 0

        for recommender in recommenders:
            try:
                logger.info(
                    f"Executing {recommender.__class__.__name__}",
                    extra={"recommender": recommender.__class__.__name__}
                )
                recommender.detect()
                total_success += 1
            except Exception as e:
                total_failed += 1
                logger.error(
                    f"Error executing {recommender.__class__.__name__}: {e}",
                    extra={"recommender": recommender.__class__.__name__},
                    exc_info=True
                )
                # Continue with next recommender instead of failing completely

        logger.info(
            "Recommendation check completed",
            extra={
                "total_recommenders": len(recommenders),
                "successful": total_success,
                "failed": total_failed
            }
        )

    except Exception as e:
        logger.error(
            f"Critical error in check_recommender: {e}",
            exc_info=True
        )
        raise
