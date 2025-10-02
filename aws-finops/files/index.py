import boto3
import json
import os
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import List, Tuple

from send_mail import send_email

# Configure structured logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

keep_instances = ['IGNORE']
keep_tag_key = os.environ['KEEP_TAG_KEY']
dry_run = os.environ.get('DRY_RUN', 'true').lower() == 'true'
from_address = os.environ['EMAIL_IDENTITY']
to_address = os.environ['TO_ADDRESS']

USED_REGIONS = [
    'us-east-1',
    'us-east-2',
    'us-west-1',
    'us-west-2',
    'eu-central-1',
    'eu-west-1'
]

deleted_resources = []
skip_delete_resources = []
notify_resources = []
check_resources = []


def process_response(response, service, resource_id):
    """
    Process the response from AWS API calls and keeps track of any deleted or failed resources.

    :param response: AWS API response.
    :param service: Name of the AWS service that was called.
    :param resource_id: ID of the AWS resource that was called.
    :return: None
    """
    if response.get("ResponseMetadata"):
        status_code = response["ResponseMetadata"]["HTTPStatusCode"]
        if status_code == 200:
            deleted_resources.append((service, resource_id))
        else:
            check_resources.append((service, resource_id))

    if response.get("DomainStatus"):
        deleted = response["DomainStatus"]["Deleted"]
        if deleted:
            deleted_resources.append((service, resource_id))
        else:
            check_resources.append((service, resource_id))


def notify_auto_clean_data():
    """
    Send email notifications about the deleted, failed, skipped or notified resources.

    :return: None
    """
    print("deleted resources", deleted_resources)
    print("notify resources", notify_resources)
    print("check resources", check_resources)
    print("skip delete resources", skip_delete_resources)

    send_email(from_address, to_address, deleted_resources, skip_delete_resources, notify_resources, check_resources)


# Delete EC2 instances

def stop_all_instances(regions):
    """
    Stop all EC2 instances

    :param regions: List of AWS region names
    """
    logger.info("====== EC2 Instances ======")
    # Stop instances in each region
    for region in regions:
        instances_to_stop = get_instances_in_region(region)
        if instances_to_stop:
            if not dry_run:
                stop_instances(instances_to_stop, region)
                deleted_resources.extend([('ec2-instance', inst_id) for inst_id in instances_to_stop])
                logger.info(f'Stopped instances: {str(instances_to_stop)}')
            else:
                skip_delete_resources.extend([('ec2-instance', inst_id) for inst_id in instances_to_stop])
                logger.info(f'DRY RUN: Would stop instances: {str(instances_to_stop)}')

def get_instances_in_region(region):
    """
    Get all non-spot running instances in a specific region

    :param region: AWS region name
    :return: List of instance ids
    """
    ec2 = boto3.client('ec2', region_name=region)
    instances = ec2.describe_instances(
        Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
    instances_to_stop = []
    for reservation in instances["Reservations"]:
        for instance in reservation["Instances"]:
            # Ignore spot instances
            if 'InstanceLifecycle' in instance and instance['InstanceLifecycle'] == 'spot':
                continue
            instance_id = instance["InstanceId"]
            instance_name = ""
            should_skip = False

            # Check for protection tags
            if "Tags" in instance:
                for tag in instance["Tags"]:
                    if tag.get("Key") == keep_tag_key and tag.get("Value") == "skip-resource":
                        should_skip = True
                        logger.info(f'Instance {instance_id} has protection tag, skipping')
                        break
                    if tag.get("Key") == "Name":
                        instance_name = tag.get("Value", "")

            if not should_skip and instance_name not in keep_instances and instance_id not in keep_instances:
                logger.info(f'Instance with ID "{instance_id}" and name "{instance_name}" will be stopped.')
                instances_to_stop.append(instance_id)
    return instances_to_stop
    
def stop_instances(instances_to_stop, region):
    """
    Stop a list of instances in a specific region
    
    :param instances_to_stop: List of instance ids
    :param region: AWS region name
    """
    ec2 = boto3.client('ec2', region_name=region)
    ec2.stop_instances(InstanceIds=instances_to_stop)


# Unmonitor EC2 instances

def unmonitor_all_instances(regions):
    """Stop detailed monitoring on all EC2 instances

    This will stop CloudWatch detailed monitoring on all instances
    in all the regions in the input

    :param regions: List of AWS region names
    """
    logger.info("====== EC2 - Unmonitor ======")

    for region in regions:
        ec2 = boto3.client('ec2', region_name=region)
        instances_to_unmonitor = []
        logger.info(f'Getting instances in region: {region}')

        # Get all running instances in the region
        response = ec2.describe_instances(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])

        for reservation in response.get('Reservations', []):
            for instance in reservation.get('Instances', []):
                instance_id = instance['InstanceId']
                monitor_state = instance.get('Monitoring', {}).get('State', 'disabled')

                if monitor_state == 'enabled':
                    logger.info(f'Instance with ID "{instance_id}" will be unmonitored.')
                    instances_to_unmonitor.append(instance_id)

        if instances_to_unmonitor:
            if not dry_run:
                ec2.unmonitor_instances(InstanceIds=instances_to_unmonitor)
                deleted_resources.extend([('ec2-monitoring', inst_id) for inst_id in instances_to_unmonitor])
                logger.info(f'Unmonitored instances: {str(instances_to_unmonitor)}')
            else:
                skip_delete_resources.extend([('ec2-monitoring', inst_id) for inst_id in instances_to_unmonitor])
                logger.info(f'DRY RUN: Would unmonitor instances: {str(instances_to_unmonitor)}')


# Delete unassociated EIPs

def release_unassociated_eip(regions):
    """Release unassociated Elastic IP addresses

    :param regions: List of AWS region names
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

                    if allocation_id:
                        if not dry_run:
                            try:
                                ec2.release_address(AllocationId=allocation_id)
                                deleted_resources.append(('eip', public_ip))
                                logger.info(f'Released EIP: {public_ip}')
                            except Exception as e:
                                logger.error(f'Failed to release EIP {public_ip}: {str(e)}')
                                check_resources.append(('eip', public_ip))
                        else:
                            skip_delete_resources.append(('eip', public_ip))
                            logger.info(f'DRY RUN: Would release EIP: {public_ip}')

        except Exception as e:
            logger.error(f'Error describing addresses in region {region}: {str(e)}')


# Delete EBS volumes

def delete_ebs_volumes(regions):
    """
    Delete all available EBS (unassociated) volumes in all the regions in the input.
    :param regions: List of AWS region names.
    """
    logger.info("====== EBS Volumes ======")

    for region in regions:
        logger.info(f'Getting all available (unused) EBS volumes in region: {region}')
        ec2 = boto3.client('ec2', region_name=region)
        eks = boto3.client('eks', region_name=region)

        try:
            response = ec2.describe_volumes()

            for volume in response['Volumes']:
                if volume['State'] == 'available':
                    volume_id = volume['VolumeId']
                    volume_size = volume.get('Size', 0)
                    delete_volume = True

                    # Check if the volume is connected to a running EKS cluster
                    tags = volume.get('Tags', [])
                    for tag in tags:
                        if tag['Key'].startswith('kubernetes.io/cluster'):
                            eks_cluster_name = tag['Key'].split('/')[2]
                            try:
                                eks.describe_cluster(name=eks_cluster_name)
                                delete_volume = False  # Don't delete volume if it's connected to existing EKS cluster
                                logger.info(f'Volume {volume_id} belongs to EKS cluster {eks_cluster_name}, skipping')
                            except eks.exceptions.ResourceNotFoundException:
                                delete_volume = True
                            break

                    if delete_volume:
                        if not dry_run:
                            try:
                                ec2.delete_volume(VolumeId=volume_id)
                                deleted_resources.append(('ebs-volume', f'{volume_id} ({volume_size}GB)'))
                                logger.info(f'Deleted EBS volume: {volume_id} ({volume_size}GB)')
                            except Exception as e:
                                logger.error(f'Failed to delete volume {volume_id}: {str(e)}')
                                check_resources.append(('ebs-volume', volume_id))
                        else:
                            skip_delete_resources.append(('ebs-volume', f'{volume_id} ({volume_size}GB)'))
                            logger.info(f'DRY RUN: Would delete EBS volume: {volume_id} ({volume_size}GB)')

        except Exception as e:
            logger.error(f'Error describing volumes in region {region}: {str(e)}')



# Delete empty load balancers

def delete_empty_load_balancers(regions):
    """
    Delete all empty (classic) load balancers. This will delete all empty
    (with no instances) classic load balancers in all the regions in the input

    :param regions: List of AWS region names
    """
    logger.info("====== Classic Load Balancers ======")

    for region in regions:
        elb = boto3.client('elb', region_name=region)

        try:
            lbs = elb.describe_load_balancers()

            for lb in lbs['LoadBalancerDescriptions']:
                if len(lb['Instances']) == 0:
                    lb_name = lb['LoadBalancerName']

                    if not dry_run:
                        try:
                            elb.delete_load_balancer(LoadBalancerName=lb_name)
                            deleted_resources.append(('classic-elb', lb_name))
                            logger.info(f'Deleted classic load balancer: {lb_name}')
                        except Exception as e:
                            logger.error(f'Failed to delete load balancer {lb_name}: {str(e)}')
                            check_resources.append(('classic-elb', lb_name))
                    else:
                        skip_delete_resources.append(('classic-elb', lb_name))
                        logger.info(f'DRY RUN: Would delete classic load balancer: {lb_name}')

        except Exception as e:
            logger.error(f'Error describing load balancers in region {region}: {str(e)}')


# Stop RDS instances

def stop_rds_instances(regions):
    """Stops RDS clusters and instances

    This will stop all RDS clusters and instances in all the regions in the input

    :param regions: List of AWS region names
    """
    logger.info("====== RDS Clusters/Instances ======")

    def stop_rds_in_region(region):
        logger.info(f'Getting RDS clusters and instances in region: {region}')
        rds_specific_region = boto3.client('rds', region_name=region)

        try:
            response = rds_specific_region.describe_db_clusters()
            for cluster in response.get('DBClusters', []):
                if cluster['Status'] == 'available':
                    cluster_id = cluster['DBClusterIdentifier']

                    if not dry_run:
                        try:
                            rds_specific_region.stop_db_cluster(DBClusterIdentifier=cluster_id)
                            deleted_resources.append(('rds-cluster', cluster_id))
                            logger.info(f'Stopped DB cluster: {cluster_id}')
                        except Exception as e:
                            logger.error(f'Failed to stop DB cluster {cluster_id}: {str(e)}')
                            check_resources.append(('rds-cluster', cluster_id))
                    else:
                        skip_delete_resources.append(('rds-cluster', cluster_id))
                        logger.info(f'DRY RUN: Would stop DB cluster: {cluster_id}')

        except Exception as e:
            logger.error(f'Error describing DB clusters in region {region}: {str(e)}')

        try:
            response = rds_specific_region.describe_db_instances()
            for instance in response.get('DBInstances', []):
                if instance['DBInstanceStatus'] == 'available':
                    instance_id = instance['DBInstanceIdentifier']

                    if not dry_run:
                        try:
                            rds_specific_region.stop_db_instance(DBInstanceIdentifier=instance_id)
                            deleted_resources.append(('rds-instance', instance_id))
                            logger.info(f'Stopped DB instance: {instance_id}')
                        except Exception as e:
                            logger.error(f'Failed to stop DB instance {instance_id}: {str(e)}')
                            check_resources.append(('rds-instance', instance_id))
                    else:
                        skip_delete_resources.append(('rds-instance', instance_id))
                        logger.info(f'DRY RUN: Would stop DB instance: {instance_id}')

        except Exception as e:
            logger.error(f'Error describing DB instances in region {region}: {str(e)}')

    with ThreadPoolExecutor(max_workers=5) as executor:
        for region in regions:
            executor.submit(stop_rds_in_region, region)



# Delete EKS nodegroups

def scale_in_eks_nodegroups(regions):
    """Scales-in EKS nodegroups to 0

    This will ensure all EKS node groups have 0 replicas in all the regions in the input

    :param regions: List of AWS region names
    """
    logger.info("====== EKS Node Groups ======")

    def scale_in_eks_nodegroups_in_region(region):
        logger.info(f'Getting EKS clusters in region {region}')
        eks_specific_region = boto3.client('eks', region_name=region)

        try:
            response_clusters = eks_specific_region.list_clusters()

            for cluster in response_clusters.get('clusters', []):
                try:
                    response_nodegroups = eks_specific_region.list_nodegroups(clusterName=cluster)

                    for ng in response_nodegroups.get('nodegroups', []):
                        try:
                            node_group_info = eks_specific_region.describe_nodegroup(
                                clusterName=cluster, nodegroupName=ng)
                            scaling_config = node_group_info['nodegroup']['scalingConfig']
                            current_desired = scaling_config.get('desiredSize', 0)

                            if current_desired > 0:
                                if not dry_run:
                                    try:
                                        # Update scaling
                                        eks_specific_region.update_nodegroup_config(
                                            clusterName=cluster,
                                            nodegroupName=ng,
                                            scalingConfig={'minSize': 0, 'desiredSize': 0}
                                        )
                                        deleted_resources.append(('eks-nodegroup', f'{cluster}/{ng}'))
                                        logger.info(f'Scaled down node group {ng} in cluster {cluster}')
                                    except Exception as e:
                                        logger.error(f'Failed to scale node group {ng} in cluster {cluster}: {str(e)}')
                                        check_resources.append(('eks-nodegroup', f'{cluster}/{ng}'))
                                else:
                                    skip_delete_resources.append(('eks-nodegroup', f'{cluster}/{ng}'))
                                    logger.info(f'DRY RUN: Would scale down node group {ng} in cluster {cluster}')

                        except Exception as e:
                            logger.error(f'Error describing nodegroup {ng} in cluster {cluster}: {str(e)}')

                except Exception as e:
                    logger.error(f'Error listing nodegroups for cluster {cluster}: {str(e)}')

        except Exception as e:
            logger.error(f'Error listing clusters in region {region}: {str(e)}')

    with ThreadPoolExecutor(max_workers=5) as executor:
        for region in regions:
            executor.submit(scale_in_eks_nodegroups_in_region, region)


# Delete Kinesis Streams

def delete_kinesis_stream(regions):
    """Delete Kinesis stream

    :param regions: List of AWS region names
    """
    logger.info("====== Kinesis Streams ======")

    def delete_kinesis_stream_in_region(region):
        logger.info(f'Getting all Kinesis streams in the region: {region}')
        kinesis_client = boto3.client('kinesis', region_name=region)

        try:
            response = kinesis_client.list_streams()

            for streamName in response.get('StreamNames', []):
                try:
                    if streamName.startswith("upsolver_"):
                        notify_resources.append(("kinesis", streamName))
                        logger.info(f'Skipped upsolver stream: {streamName}')
                    else:
                        if not dry_run:
                            try:
                                kinesis_client.delete_stream(
                                    StreamName=streamName,
                                    EnforceConsumerDeletion=True
                                )
                                deleted_resources.append(("kinesis-stream", streamName))
                                logger.info(f'Deleted Kinesis stream: {streamName}')
                            except Exception as e:
                                logger.error(f'Failed to delete kinesis stream {streamName}: {str(e)}')
                                check_resources.append(("kinesis-stream", streamName))
                        else:
                            skip_delete_resources.append(("kinesis-stream", streamName))
                            logger.info(f'DRY RUN: Would delete Kinesis stream: {streamName}')

                except Exception as e:
                    logger.error(f'Error processing kinesis stream {streamName}: {str(e)}')

        except Exception as e:
            logger.error(f'Error listing kinesis streams in region {region}: {str(e)}')

    with ThreadPoolExecutor(max_workers=5) as executor:
        for region in regions:
            executor.submit(delete_kinesis_stream_in_region, region)


# Delete MSK clusters

def delete_msk_clusters(regions):
    """Delete MSK (Kafka) clusters

    :param regions: List of AWS region names
    """
    logger.info("====== MSK Clusters ======")

    def delete_msk_in_region(region):
        logger.info(f'Getting all MSK clusters in the region: {region}')
        kafka_client = boto3.client('kafka', region_name=region)

        try:
            response = kafka_client.list_clusters()

            for cluster in response.get('ClusterInfoList', []):
                cluster_arn = cluster.get('ClusterArn')
                cluster_name = cluster.get('ClusterName')

                if not dry_run:
                    try:
                        kafka_client.delete_cluster(ClusterArn=cluster_arn)
                        deleted_resources.append(("msk-cluster", cluster_name))
                        logger.info(f'Deleted MSK cluster: {cluster_name}')
                    except Exception as e:
                        logger.error(f'Failed to delete MSK cluster {cluster_name}: {str(e)}')
                        check_resources.append(("msk-cluster", cluster_name))
                else:
                    skip_delete_resources.append(("msk-cluster", cluster_name))
                    logger.info(f'DRY RUN: Would delete MSK cluster: {cluster_name}')

        except Exception as e:
            logger.error(f'Error listing MSK clusters in region {region}: {str(e)}')

    with ThreadPoolExecutor(max_workers=5) as executor:
        for region in regions:
            executor.submit(delete_msk_in_region, region)



# Delete OpenSearch domains

def delete_domain(regions):
    """Delete OpenSearch domains

    :param regions: List of AWS region names
    """
    logger.info("====== OpenSearch domains ======")

    def delete_domain_in_region(region):
        logger.info(f'Getting all OpenSearch domains in the region: {region}')
        domain_client = boto3.client('opensearch', region_name=region)

        try:
            response = domain_client.list_domain_names(EngineType='OpenSearch')

            for domain_info in response.get('DomainNames', []):
                domain_name = domain_info.get('DomainName')

                if not dry_run:
                    try:
                        domain_client.delete_domain(DomainName=domain_name)
                        deleted_resources.append(("opensearch-domain", domain_name))
                        logger.info(f'Deleted OpenSearch domain: {domain_name}')
                    except Exception as e:
                        logger.error(f'Failed to delete OpenSearch domain {domain_name}: {str(e)}')
                        check_resources.append(("opensearch-domain", domain_name))
                else:
                    skip_delete_resources.append(("opensearch-domain", domain_name))
                    logger.info(f'DRY RUN: Would delete OpenSearch domain: {domain_name}')

        except Exception as e:
            logger.error(f'Error listing OpenSearch domains in region {region}: {str(e)}')

    with ThreadPoolExecutor(max_workers=5) as executor:
        for region in regions:
            executor.submit(delete_domain_in_region, region)

# Tag instances with CreatedOn date

def tag_instances(regions):
    """Add "CreatedOn" tag on resources

    This will check the resource creation date against AWS Config
    and add it as a tag to the resource

    :param regions: List of AWS region names
    """
    logger.info("====== Tagging Instances ======")

    def process_instance(instance, ec2_specific_region, config_specific_region):
        # Ignore spot instances
        if 'InstanceLifecycle' in instance and instance['InstanceLifecycle'] == 'spot':
            return

        # Skip instance if tag already present
        found_tag = False
        if "Tags" in instance:
            for tag in instance["Tags"]:
                if tag["Key"] == "CreatedOn":
                    found_tag = True
                    break
        if found_tag:
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

                response = ec2_specific_region.describe_instances()
                if "Reservations" in response:
                    for reservation in response["Reservations"]:
                        if "Instances" in reservation:
                            instances = reservation["Instances"]
                            executor.map(process_instance, instances,
                                       [ec2_specific_region]*len(instances),
                                       [config_specific_region]*len(instances))

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

    check_all_regions = os.environ.get('CHECK_ALL_REGIONS', 'false').lower() == 'true'
    if check_all_regions:
        regions = get_aws_regions()
    else:
        regions = USED_REGIONS

    logger.info(f"Scanning regions: {', '.join(regions)}")

    try:
        # Execute all cleanup operations
        stop_all_instances(regions)
        tag_instances(regions)
        unmonitor_all_instances(regions)
        release_unassociated_eip(regions)
        delete_ebs_volumes(regions)
        delete_empty_load_balancers(regions)
        stop_rds_instances(regions)
        scale_in_eks_nodegroups(regions)
        delete_kinesis_stream(regions)
        delete_msk_clusters(regions)
        delete_domain(regions)

        # Send email notification with results
        notify_auto_clean_data()

        logger.info("====== AWS FinOps Resource Cleanup Completed ======")
        logger.info(f"Total resources processed - Deleted: {len(deleted_resources)}, "
                   f"Skipped: {len(skip_delete_resources)}, "
                   f"Failed: {len(check_resources)}, "
                   f"Notified: {len(notify_resources)}")

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Success!',
                'dry_run': dry_run,
                'deleted': len(deleted_resources),
                'skipped': len(skip_delete_resources),
                'failed': len(check_resources),
                'notified': len(notify_resources)
            })
        }

    except Exception as e:
        logger.error(f"Error in lambda_handler: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }