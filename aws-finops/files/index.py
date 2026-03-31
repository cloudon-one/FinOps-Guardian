import boto3
import json
import os
import logging
import re
import time
import threading
from functools import wraps
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Tuple, Optional, Callable
from botocore.exceptions import ClientError

from send_mail import send_email

# Configure structured logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def validate_email(email: str) -> bool:
    """Validate email address format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def get_validated_env(key: str, default: Optional[str] = None, required: bool = True) -> Optional[str]:
    """Get and validate environment variable

    :param key: Environment variable name
    :param default: Default value if not set
    :param required: Whether variable is required
    :return: Environment variable value
    :raises: ValueError if required variable is missing or invalid
    """
    value = os.environ.get(key, default)

    if required and not value:
        raise ValueError(f"Required environment variable '{key}' is not set")

    # Validate specific environment variables
    if key in ['EMAIL_IDENTITY', 'TO_ADDRESS'] and value:
        if not validate_email(value):
            raise ValueError(f"Invalid email format for '{key}': {value}")

    if key == 'DRY_RUN' and value:
        if value.lower() not in ['true', 'false']:
            raise ValueError(f"DRY_RUN must be 'true' or 'false', got: {value}")

    if key == 'CHECK_ALL_REGIONS' and value:
        if value.lower() not in ['true', 'false']:
            raise ValueError(f"CHECK_ALL_REGIONS must be 'true' or 'false', got: {value}")

    return value


def retry_with_backoff(max_retries: int = 3, initial_delay: float = 1.0, backoff_factor: float = 2.0):
    """Decorator to retry function with exponential backoff

    :param max_retries: Maximum number of retry attempts
    :param initial_delay: Initial delay in seconds
    :param backoff_factor: Multiplier for delay on each retry
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            delay = initial_delay
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except ClientError as e:
                    error_code = e.response.get('Error', {}).get('Code', '')
                    last_exception = e

                    # Don't retry on non-retryable errors
                    if error_code in ['ValidationException', 'InvalidParameterException', 'AccessDenied']:
                        logger.error(f"{func.__name__} failed with non-retryable error: {error_code}")
                        raise

                    # Throttling errors - retry with backoff
                    if error_code in ['Throttling', 'TooManyRequestsException', 'RequestLimitExceeded']:
                        if attempt < max_retries:
                            logger.warning(f"{func.__name__} throttled, retrying in {delay}s (attempt {attempt + 1}/{max_retries})")
                            time.sleep(delay)
                            delay *= backoff_factor
                            continue
                        else:
                            logger.error(f"{func.__name__} failed after {max_retries} retries: {str(e)}")
                            raise

                    # Other client errors - retry with backoff
                    if attempt < max_retries:
                        logger.warning(f"{func.__name__} failed, retrying in {delay}s (attempt {attempt + 1}/{max_retries}): {str(e)}")
                        time.sleep(delay)
                        delay *= backoff_factor
                    else:
                        logger.error(f"{func.__name__} failed after {max_retries} retries: {str(e)}")
                        raise

                except Exception as e:
                    logger.error(f"{func.__name__} failed with unexpected error: {str(e)}")
                    raise

            if last_exception:
                raise last_exception

        return wrapper
    return decorator


# Validate and load environment variables
try:
    keep_tag_key = get_validated_env('KEEP_TAG_KEY', default='auto-deletion', required=False)
    keep_tag_value = get_validated_env('KEEP_TAG_VALUE', default='skip-resource', required=False)
    dry_run = get_validated_env('DRY_RUN', default='true', required=False).lower() == 'true'
    from_address = get_validated_env('EMAIL_IDENTITY', required=True)
    to_address = get_validated_env('TO_ADDRESS', required=True)

    logger.info(f"Configuration loaded - DRY_RUN: {dry_run}, KEEP_TAG_KEY: {keep_tag_key}")

except ValueError as e:
    logger.error(f"Configuration error: {str(e)}")
    raise

# Default regions if not specified
DEFAULT_REGIONS = [
    'us-east-1',
    'us-east-2',
    'us-west-1',
    'us-west-2',
    'eu-north-1',
    'eu-central-1',
    'eu-west-1'
]

# Load regions from environment or use defaults
REGIONS_ENV = get_validated_env('REGIONS', default='', required=False)
if REGIONS_ENV:
    USED_REGIONS = [r.strip() for r in REGIONS_ENV.split(',') if r.strip()]
    logger.info(f"Using custom regions from environment: {USED_REGIONS}")
else:
    USED_REGIONS = DEFAULT_REGIONS
    logger.info(f"Using default regions: {USED_REGIONS}")


class ResourceTracker:
    """Thread-safe tracker for resource cleanup results."""

    def __init__(self):
        self._lock = threading.Lock()
        self.deleted_resources: List[Tuple[str, str]] = []
        self.skip_delete_resources: List[Tuple[str, str]] = []
        self.notify_resources: List[Tuple[str, str]] = []
        self.check_resources: List[Tuple[str, str]] = []

    def add_deleted(self, service: str, resource_id: str):
        with self._lock:
            self.deleted_resources.append((service, resource_id))

    def add_skipped(self, service: str, resource_id: str):
        with self._lock:
            self.skip_delete_resources.append((service, resource_id))

    def add_notify(self, service: str, resource_id: str):
        with self._lock:
            self.notify_resources.append((service, resource_id))

    def add_failed(self, service: str, resource_id: str):
        with self._lock:
            self.check_resources.append((service, resource_id))


def _has_protection_tag(tags: list) -> bool:
    """Check if resource has the protection tag.

    :param tags: List of tag dicts with Key/Value
    :return: True if resource is protected
    """
    for tag in tags:
        if tag.get("Key") == keep_tag_key and tag.get("Value") == keep_tag_value:
            return True
    return False


def notify_auto_clean_data(tracker: ResourceTracker):
    """Send email notifications about the deleted, failed, skipped or notified resources."""
    logger.info(f"deleted resources: {tracker.deleted_resources}")
    logger.info(f"notify resources: {tracker.notify_resources}")
    logger.info(f"check resources: {tracker.check_resources}")
    logger.info(f"skip delete resources: {tracker.skip_delete_resources}")

    send_email(from_address, to_address, tracker.deleted_resources,
               tracker.skip_delete_resources, tracker.notify_resources, tracker.check_resources)


# Delete EC2 instances

@retry_with_backoff()
def stop_instances(instances_to_stop, region):
    """Stop a list of instances in a specific region

    :param instances_to_stop: List of instance ids
    :param region: AWS region name
    """
    ec2 = boto3.client('ec2', region_name=region)
    ec2.stop_instances(InstanceIds=instances_to_stop)


def stop_all_instances(regions, tracker: ResourceTracker):
    """Stop all EC2 instances

    :param regions: List of AWS region names
    :param tracker: ResourceTracker instance
    """
    logger.info("====== EC2 Instances ======")
    for region in regions:
        instances_to_stop = get_instances_in_region(region, tracker)
        if instances_to_stop:
            if not dry_run:
                try:
                    stop_instances(instances_to_stop, region)
                    for inst_id in instances_to_stop:
                        tracker.add_deleted('ec2-instance', inst_id)
                    logger.info(f'Stopped instances: {str(instances_to_stop)}')
                except Exception as e:
                    logger.error(f'Failed to stop instances in {region}: {str(e)}')
                    for inst_id in instances_to_stop:
                        tracker.add_failed('ec2-instance', inst_id)
            else:
                for inst_id in instances_to_stop:
                    tracker.add_skipped('ec2-instance', inst_id)
                logger.info(f'DRY RUN: Would stop instances: {str(instances_to_stop)}')


def get_instances_in_region(region, tracker: ResourceTracker):
    """Get all non-spot running instances in a specific region using pagination

    :param region: AWS region name
    :param tracker: ResourceTracker instance
    :return: List of instance ids
    """
    ec2 = boto3.client('ec2', region_name=region)
    instances_to_stop = []

    paginator = ec2.get_paginator('describe_instances')
    for page in paginator.paginate(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}]):
        for reservation in page["Reservations"]:
            for instance in reservation["Instances"]:
                # Ignore spot instances
                if instance.get('InstanceLifecycle') == 'spot':
                    continue
                instance_id = instance["InstanceId"]
                instance_name = ""

                tags = instance.get("Tags", [])
                if _has_protection_tag(tags):
                    logger.info(f'Instance {instance_id} has protection tag, skipping')
                    continue

                for tag in tags:
                    if tag.get("Key") == "Name":
                        instance_name = tag.get("Value", "")

                logger.info(f'Instance with ID "{instance_id}" and name "{instance_name}" will be stopped.')
                instances_to_stop.append(instance_id)

    return instances_to_stop


# Unmonitor EC2 instances

def unmonitor_all_instances(regions, tracker: ResourceTracker):
    """Stop detailed monitoring on all EC2 instances

    :param regions: List of AWS region names
    :param tracker: ResourceTracker instance
    """
    logger.info("====== EC2 - Unmonitor ======")

    for region in regions:
        ec2 = boto3.client('ec2', region_name=region)
        instances_to_unmonitor = []
        logger.info(f'Getting instances in region: {region}')

        paginator = ec2.get_paginator('describe_instances')
        for page in paginator.paginate(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}]):
            for reservation in page.get('Reservations', []):
                for instance in reservation.get('Instances', []):
                    instance_id = instance['InstanceId']
                    monitor_state = instance.get('Monitoring', {}).get('State', 'disabled')

                    if monitor_state == 'enabled':
                        logger.info(f'Instance with ID "{instance_id}" will be unmonitored.')
                        instances_to_unmonitor.append(instance_id)

        if instances_to_unmonitor:
            if not dry_run:
                ec2.unmonitor_instances(InstanceIds=instances_to_unmonitor)
                for inst_id in instances_to_unmonitor:
                    tracker.add_deleted('ec2-monitoring', inst_id)
                logger.info(f'Unmonitored instances: {str(instances_to_unmonitor)}')
            else:
                for inst_id in instances_to_unmonitor:
                    tracker.add_skipped('ec2-monitoring', inst_id)
                logger.info(f'DRY RUN: Would unmonitor instances: {str(instances_to_unmonitor)}')


# Delete unassociated EIPs

def release_unassociated_eip(regions, tracker: ResourceTracker):
    """Release unassociated Elastic IP addresses

    :param regions: List of AWS region names
    :param tracker: ResourceTracker instance
    """
    logger.info("====== Elastic IPs ======")

    for region in regions:
        ec2 = boto3.client('ec2', region_name=region)
        logger.info(f'Getting unassociated EIPs in region: {region}')

        try:
            addresses = ec2.describe_addresses()

            for address in addresses.get('Addresses', []):
                # Check if EIP is not associated with any instance
                if 'AssociationId' not in address:
                    allocation_id = address.get('AllocationId')
                    public_ip = address.get('PublicIp')

                    # Check protection tag
                    if _has_protection_tag(address.get('Tags', [])):
                        logger.info(f'EIP {public_ip} has protection tag, skipping')
                        continue

                    if allocation_id:
                        if not dry_run:
                            try:
                                ec2.release_address(AllocationId=allocation_id)
                                tracker.add_deleted('eip', public_ip)
                                logger.info(f'Released EIP: {public_ip}')
                            except Exception as e:
                                logger.error(f'Failed to release EIP {public_ip}: {str(e)}')
                                tracker.add_failed('eip', public_ip)
                        else:
                            tracker.add_skipped('eip', public_ip)
                            logger.info(f'DRY RUN: Would release EIP: {public_ip}')

        except Exception as e:
            logger.error(f'Error describing addresses in region {region}: {str(e)}')


# Delete EBS volumes

def delete_ebs_volumes(regions, tracker: ResourceTracker):
    """Delete all available EBS (unassociated) volumes using pagination.

    :param regions: List of AWS region names
    :param tracker: ResourceTracker instance
    """
    logger.info("====== EBS Volumes ======")

    for region in regions:
        logger.info(f'Getting all available (unused) EBS volumes in region: {region}')
        ec2 = boto3.client('ec2', region_name=region)
        eks = boto3.client('eks', region_name=region)

        try:
            paginator = ec2.get_paginator('describe_volumes')
            for page in paginator.paginate(Filters=[{'Name': 'status', 'Values': ['available']}]):
                for volume in page['Volumes']:
                    volume_id = volume['VolumeId']
                    volume_size = volume.get('Size', 0)
                    delete_volume = True

                    # Check protection tag
                    tags = volume.get('Tags', [])
                    if _has_protection_tag(tags):
                        logger.info(f'Volume {volume_id} has protection tag, skipping')
                        continue

                    # Check if the volume is connected to a running EKS cluster
                    for tag in tags:
                        if tag['Key'].startswith('kubernetes.io/cluster'):
                            eks_cluster_name = tag['Key'].split('/')[2]
                            try:
                                eks.describe_cluster(name=eks_cluster_name)
                                delete_volume = False
                                logger.info(f'Volume {volume_id} belongs to EKS cluster {eks_cluster_name}, skipping')
                            except eks.exceptions.ResourceNotFoundException:
                                delete_volume = True
                            except ClientError as e:
                                logger.warning(f'Error checking EKS cluster {eks_cluster_name}: {str(e)}')
                                delete_volume = False
                            break

                    if delete_volume:
                        if not dry_run:
                            try:
                                ec2.delete_volume(VolumeId=volume_id)
                                tracker.add_deleted('ebs-volume', f'{volume_id} ({volume_size}GB)')
                                logger.info(f'Deleted EBS volume: {volume_id} ({volume_size}GB)')
                            except Exception as e:
                                logger.error(f'Failed to delete volume {volume_id}: {str(e)}')
                                tracker.add_failed('ebs-volume', volume_id)
                        else:
                            tracker.add_skipped('ebs-volume', f'{volume_id} ({volume_size}GB)')
                            logger.info(f'DRY RUN: Would delete EBS volume: {volume_id} ({volume_size}GB)')

        except Exception as e:
            logger.error(f'Error describing volumes in region {region}: {str(e)}')



# Delete empty load balancers

def delete_empty_load_balancers(regions, tracker: ResourceTracker):
    """Delete all empty (classic) load balancers with tag protection.

    :param regions: List of AWS region names
    :param tracker: ResourceTracker instance
    """
    logger.info("====== Classic Load Balancers ======")

    for region in regions:
        elb = boto3.client('elb', region_name=region)

        try:
            paginator = elb.get_paginator('describe_load_balancers')
            for page in paginator.paginate():
                for lb in page['LoadBalancerDescriptions']:
                    if len(lb['Instances']) == 0:
                        lb_name = lb['LoadBalancerName']

                        # Check protection tag
                        try:
                            tag_response = elb.describe_tags(LoadBalancerNames=[lb_name])
                            for tag_desc in tag_response.get('TagDescriptions', []):
                                if _has_protection_tag(tag_desc.get('Tags', [])):
                                    logger.info(f'Load balancer {lb_name} has protection tag, skipping')
                                    continue
                        except Exception:
                            pass

                        if not dry_run:
                            try:
                                elb.delete_load_balancer(LoadBalancerName=lb_name)
                                tracker.add_deleted('classic-elb', lb_name)
                                logger.info(f'Deleted classic load balancer: {lb_name}')
                            except Exception as e:
                                logger.error(f'Failed to delete load balancer {lb_name}: {str(e)}')
                                tracker.add_failed('classic-elb', lb_name)
                        else:
                            tracker.add_skipped('classic-elb', lb_name)
                            logger.info(f'DRY RUN: Would delete classic load balancer: {lb_name}')

        except Exception as e:
            logger.error(f'Error describing load balancers in region {region}: {str(e)}')


# Stop RDS instances

def stop_rds_instances(regions, tracker: ResourceTracker):
    """Stops RDS clusters and instances using pagination.

    :param regions: List of AWS region names
    :param tracker: ResourceTracker instance
    """
    logger.info("====== RDS Clusters/Instances ======")

    def stop_rds_in_region(region):
        logger.info(f'Getting RDS clusters and instances in region: {region}')
        rds = boto3.client('rds', region_name=region)

        try:
            paginator = rds.get_paginator('describe_db_clusters')
            for page in paginator.paginate():
                for cluster in page.get('DBClusters', []):
                    if cluster['Status'] == 'available':
                        cluster_id = cluster['DBClusterIdentifier']

                        if not dry_run:
                            try:
                                rds.stop_db_cluster(DBClusterIdentifier=cluster_id)
                                tracker.add_deleted('rds-cluster', cluster_id)
                                logger.info(f'Stopped DB cluster: {cluster_id}')
                            except Exception as e:
                                logger.error(f'Failed to stop DB cluster {cluster_id}: {str(e)}')
                                tracker.add_failed('rds-cluster', cluster_id)
                        else:
                            tracker.add_skipped('rds-cluster', cluster_id)
                            logger.info(f'DRY RUN: Would stop DB cluster: {cluster_id}')

        except Exception as e:
            logger.error(f'Error describing DB clusters in region {region}: {str(e)}')

        try:
            paginator = rds.get_paginator('describe_db_instances')
            for page in paginator.paginate():
                for instance in page.get('DBInstances', []):
                    if instance['DBInstanceStatus'] == 'available':
                        instance_id = instance['DBInstanceIdentifier']

                        if not dry_run:
                            try:
                                rds.stop_db_instance(DBInstanceIdentifier=instance_id)
                                tracker.add_deleted('rds-instance', instance_id)
                                logger.info(f'Stopped DB instance: {instance_id}')
                            except Exception as e:
                                logger.error(f'Failed to stop DB instance {instance_id}: {str(e)}')
                                tracker.add_failed('rds-instance', instance_id)
                        else:
                            tracker.add_skipped('rds-instance', instance_id)
                            logger.info(f'DRY RUN: Would stop DB instance: {instance_id}')

        except Exception as e:
            logger.error(f'Error describing DB instances in region {region}: {str(e)}')

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(stop_rds_in_region, region) for region in regions]
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                logger.error(f'Error in RDS cleanup thread: {str(e)}')



# Scale in EKS nodegroups

def scale_in_eks_nodegroups(regions, tracker: ResourceTracker):
    """Scales-in EKS nodegroups to 0

    :param regions: List of AWS region names
    :param tracker: ResourceTracker instance
    """
    logger.info("====== EKS Node Groups ======")

    def scale_in_eks_nodegroups_in_region(region):
        logger.info(f'Getting EKS clusters in region {region}')
        eks = boto3.client('eks', region_name=region)

        try:
            paginator = eks.get_paginator('list_clusters')
            for page in paginator.paginate():
                for cluster in page.get('clusters', []):
                    try:
                        ng_paginator = eks.get_paginator('list_nodegroups')
                        for ng_page in ng_paginator.paginate(clusterName=cluster):
                            for ng in ng_page.get('nodegroups', []):
                                try:
                                    node_group_info = eks.describe_nodegroup(
                                        clusterName=cluster, nodegroupName=ng)
                                    scaling_config = node_group_info['nodegroup']['scalingConfig']
                                    current_desired = scaling_config.get('desiredSize', 0)

                                    if current_desired > 0:
                                        if not dry_run:
                                            try:
                                                eks.update_nodegroup_config(
                                                    clusterName=cluster,
                                                    nodegroupName=ng,
                                                    scalingConfig={
                                                        'minSize': 0,
                                                        'desiredSize': 0,
                                                        'maxSize': scaling_config.get('maxSize', 0)
                                                    }
                                                )
                                                tracker.add_deleted('eks-nodegroup', f'{cluster}/{ng}')
                                                logger.info(f'Scaled down node group {ng} in cluster {cluster}')
                                            except Exception as e:
                                                logger.error(f'Failed to scale node group {ng} in cluster {cluster}: {str(e)}')
                                                tracker.add_failed('eks-nodegroup', f'{cluster}/{ng}')
                                        else:
                                            tracker.add_skipped('eks-nodegroup', f'{cluster}/{ng}')
                                            logger.info(f'DRY RUN: Would scale down node group {ng} in cluster {cluster}')

                                except Exception as e:
                                    logger.error(f'Error describing nodegroup {ng} in cluster {cluster}: {str(e)}')

                    except Exception as e:
                        logger.error(f'Error listing nodegroups for cluster {cluster}: {str(e)}')

        except Exception as e:
            logger.error(f'Error listing clusters in region {region}: {str(e)}')

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(scale_in_eks_nodegroups_in_region, region) for region in regions]
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                logger.error(f'Error in EKS cleanup thread: {str(e)}')


# Delete Kinesis Streams

def delete_kinesis_stream(regions, tracker: ResourceTracker):
    """Delete Kinesis streams using pagination.

    :param regions: List of AWS region names
    :param tracker: ResourceTracker instance
    """
    logger.info("====== Kinesis Streams ======")

    def delete_kinesis_stream_in_region(region):
        logger.info(f'Getting all Kinesis streams in the region: {region}')
        kinesis_client = boto3.client('kinesis', region_name=region)

        try:
            paginator = kinesis_client.get_paginator('list_streams')
            for page in paginator.paginate():
                for streamName in page.get('StreamNames', []):
                    try:
                        if streamName.startswith("upsolver_"):
                            tracker.add_notify("kinesis", streamName)
                            logger.info(f'Skipped upsolver stream: {streamName}')
                        else:
                            if not dry_run:
                                try:
                                    kinesis_client.delete_stream(
                                        StreamName=streamName,
                                        EnforceConsumerDeletion=True
                                    )
                                    tracker.add_deleted("kinesis-stream", streamName)
                                    logger.info(f'Deleted Kinesis stream: {streamName}')
                                except Exception as e:
                                    logger.error(f'Failed to delete kinesis stream {streamName}: {str(e)}')
                                    tracker.add_failed("kinesis-stream", streamName)
                            else:
                                tracker.add_skipped("kinesis-stream", streamName)
                                logger.info(f'DRY RUN: Would delete Kinesis stream: {streamName}')

                    except Exception as e:
                        logger.error(f'Error processing kinesis stream {streamName}: {str(e)}')

        except Exception as e:
            logger.error(f'Error listing kinesis streams in region {region}: {str(e)}')

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(delete_kinesis_stream_in_region, region) for region in regions]
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                logger.error(f'Error in Kinesis cleanup thread: {str(e)}')


# Delete MSK clusters

def delete_msk_clusters(regions, tracker: ResourceTracker):
    """Delete MSK (Kafka) clusters with state filtering and pagination.

    :param regions: List of AWS region names
    :param tracker: ResourceTracker instance
    """
    logger.info("====== MSK Clusters ======")

    def delete_msk_in_region(region):
        logger.info(f'Getting all MSK clusters in the region: {region}')
        kafka_client = boto3.client('kafka', region_name=region)

        try:
            paginator = kafka_client.get_paginator('list_clusters')
            for page in paginator.paginate():
                for cluster in page.get('ClusterInfoList', []):
                    cluster_arn = cluster.get('ClusterArn')
                    cluster_name = cluster.get('ClusterName')
                    cluster_state = cluster.get('State', '')

                    # Only delete clusters in ACTIVE state
                    if cluster_state not in ('ACTIVE',):
                        logger.info(f'MSK cluster {cluster_name} in state {cluster_state}, skipping')
                        continue

                    if not dry_run:
                        try:
                            kafka_client.delete_cluster(ClusterArn=cluster_arn)
                            tracker.add_deleted("msk-cluster", cluster_name)
                            logger.info(f'Deleted MSK cluster: {cluster_name}')
                        except Exception as e:
                            logger.error(f'Failed to delete MSK cluster {cluster_name}: {str(e)}')
                            tracker.add_failed("msk-cluster", cluster_name)
                    else:
                        tracker.add_skipped("msk-cluster", cluster_name)
                        logger.info(f'DRY RUN: Would delete MSK cluster: {cluster_name}')

        except Exception as e:
            logger.error(f'Error listing MSK clusters in region {region}: {str(e)}')

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(delete_msk_in_region, region) for region in regions]
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                logger.error(f'Error in MSK cleanup thread: {str(e)}')



# Delete OpenSearch domains

def delete_domain(regions, tracker: ResourceTracker):
    """Delete OpenSearch domains with state filtering.

    :param regions: List of AWS region names
    :param tracker: ResourceTracker instance
    """
    logger.info("====== OpenSearch domains ======")

    def delete_domain_in_region(region):
        logger.info(f'Getting all OpenSearch domains in the region: {region}')
        domain_client = boto3.client('opensearch', region_name=region)

        try:
            response = domain_client.list_domain_names(EngineType='OpenSearch')

            for domain_info in response.get('DomainNames', []):
                domain_name = domain_info.get('DomainName')

                # Check domain is not in a transitional state
                try:
                    domain_status = domain_client.describe_domain(DomainName=domain_name)
                    if domain_status['DomainStatus'].get('Processing', False):
                        logger.info(f'OpenSearch domain {domain_name} is processing, skipping')
                        continue
                    if domain_status['DomainStatus'].get('Deleted', False):
                        logger.info(f'OpenSearch domain {domain_name} already deleting, skipping')
                        continue
                except Exception as e:
                    logger.warning(f'Error checking domain status for {domain_name}: {str(e)}')
                    continue

                if not dry_run:
                    try:
                        domain_client.delete_domain(DomainName=domain_name)
                        tracker.add_deleted("opensearch-domain", domain_name)
                        logger.info(f'Deleted OpenSearch domain: {domain_name}')
                    except Exception as e:
                        logger.error(f'Failed to delete OpenSearch domain {domain_name}: {str(e)}')
                        tracker.add_failed("opensearch-domain", domain_name)
                else:
                    tracker.add_skipped("opensearch-domain", domain_name)
                    logger.info(f'DRY RUN: Would delete OpenSearch domain: {domain_name}')

        except Exception as e:
            logger.error(f'Error listing OpenSearch domains in region {region}: {str(e)}')

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(delete_domain_in_region, region) for region in regions]
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                logger.error(f'Error in OpenSearch cleanup thread: {str(e)}')

# Tag instances with CreatedOn date

def tag_instances(regions, tracker: ResourceTracker):
    """Add "CreatedOn" tag on resources

    :param regions: List of AWS region names
    :param tracker: ResourceTracker instance
    """
    logger.info("====== Tagging Instances ======")

    def process_instance(instance, ec2_specific_region, config_specific_region):
        # Ignore spot instances
        if instance.get('InstanceLifecycle') == 'spot':
            return

        # Skip instance if tag already present
        if "Tags" in instance:
            for tag in instance["Tags"]:
                if tag["Key"] == "CreatedOn":
                    return

        instance_id = instance["InstanceId"]
        try:
            response = config_specific_region.get_resource_config_history(
                resourceType='AWS::EC2::Instance',
                resourceId=instance_id)

            if response.get('configurationItems'):
                created_on = response['configurationItems'][0]['resourceCreationTime']
                created_on = created_on.strftime("%d/%m/%Y")
                logger.info(f'Instance {instance_id} created on {created_on}')

                # Create tag on instance
                if not dry_run:
                    ec2_specific_region.create_tags(
                        Resources=[instance_id],
                        Tags=[{'Key': 'CreatedOn', 'Value': created_on}]
                    )
                    logger.info(f'Tagged instance {instance_id} with CreatedOn: {created_on}')
                else:
                    logger.info(f'DRY RUN: Would tag instance {instance_id} with CreatedOn: {created_on}')

        except Exception as e:
            logger.error(f'Error tagging instance {instance_id}: {str(e)}')

    with ThreadPoolExecutor(max_workers=5) as executor:
        for region in regions:
            logger.info(f'Getting instances in region: {region}')
            ec2_specific_region = boto3.client('ec2', region_name=region)
            config_specific_region = boto3.client('config', region_name=region)

            try:
                # Check if there are discovered resources in AWS Config
                response = config_specific_region.get_discovered_resource_counts()
                if response.get('totalDiscoveredResources', 0) == 0:
                    continue

                paginator = ec2_specific_region.get_paginator('describe_instances')
                for page in paginator.paginate():
                    if "Reservations" in page:
                        for reservation in page["Reservations"]:
                            if "Instances" in reservation:
                                futures = []
                                for instance in reservation["Instances"]:
                                    futures.append(executor.submit(
                                        process_instance, instance,
                                        ec2_specific_region, config_specific_region))
                                for future in as_completed(futures):
                                    try:
                                        future.result()
                                    except Exception as e:
                                        logger.error(f'Error in tagging thread: {str(e)}')

            except Exception as e:
                logger.error(f'Error processing instances in region {region}: {str(e)}')


# Get all AWS regions

def get_aws_regions():
    """Get list of all enabled AWS regions

    :return: List of AWS region names
    """
    ec2 = boto3.client('ec2', region_name='us-east-1')
    try:
        response = ec2.describe_regions(AllRegions=False)
        regions = [region['RegionName'] for region in response['Regions']]
        logger.info(f'Found {len(regions)} enabled regions')
        return regions
    except Exception as e:
        logger.error(f'Error getting AWS regions: {str(e)}')
        return USED_REGIONS  # Fallback to default regions

def lambda_handler(event, context):
    """Main Lambda handler function

    :param event: Lambda event object
    :param context: Lambda context object
    :return: Response with status code and body
    """
    logger.info("====== AWS FinOps Resource Cleanup Started ======")
    logger.info(f"Dry run mode: {dry_run}")

    # Create fresh tracker for each invocation to avoid warm-start pollution
    tracker = ResourceTracker()

    check_all_regions = os.environ.get('CHECK_ALL_REGIONS', 'false').lower() == 'true'
    if check_all_regions:
        regions = get_aws_regions()
    else:
        regions = USED_REGIONS

    logger.info(f"Scanning regions: {', '.join(regions)}")

    try:
        # Execute all cleanup operations
        stop_all_instances(regions, tracker)
        tag_instances(regions, tracker)
        unmonitor_all_instances(regions, tracker)
        release_unassociated_eip(regions, tracker)
        delete_ebs_volumes(regions, tracker)
        delete_empty_load_balancers(regions, tracker)
        stop_rds_instances(regions, tracker)
        scale_in_eks_nodegroups(regions, tracker)
        delete_kinesis_stream(regions, tracker)
        delete_msk_clusters(regions, tracker)
        delete_domain(regions, tracker)

        # Send email notification with results
        notify_auto_clean_data(tracker)

        logger.info("====== AWS FinOps Resource Cleanup Completed ======")
        logger.info(f"Total resources processed - Deleted: {len(tracker.deleted_resources)}, "
                   f"Skipped: {len(tracker.skip_delete_resources)}, "
                   f"Failed: {len(tracker.check_resources)}, "
                   f"Notified: {len(tracker.notify_resources)}")

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Success!',
                'dry_run': dry_run,
                'deleted': len(tracker.deleted_resources),
                'skipped': len(tracker.skip_delete_resources),
                'failed': len(tracker.check_resources),
                'notified': len(tracker.notify_resources)
            })
        }

    except Exception as e:
        logger.error(f"Error in lambda_handler: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
