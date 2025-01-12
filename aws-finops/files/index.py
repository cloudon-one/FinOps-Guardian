import boto3
import json
import os

from send_mail import send_email


keep_instances = ['IGNORE']
keep_tag_key = os.environ['KEEP_TAG_KEY']
dry_run = os.environ['DRY_RUN']
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

import boto3

def stop_all_instances(regions):
    """
    Stop all EC2 instances
    
    :param regions: List of AWS region names
    """
    print("====== EC2 ======")
    # Stop instances in each region
    for region in regions:
        instances_to_stop = get_instances_in_region(region)
        if instances_to_stop:
            if dry_run == 'false':
                stop_instances(instances_to_stop, region)
            print(f'[INFO]: Stopped instances: {str(instances_to_stop)}')

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
            if "Tags" in instance:
                for tag in instance["Tags"]:
                    if tag.get("auto-deletion") == "skip-resource":
                        instance_name = tag["Value"]
            if instance_name not in keep_instances and instance_id not in keep_instances:
                print(
                    f'[INFO]: Instance with ID "{instance_id}" and name "{instance_name}" will be stopped.')
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

import boto3

def unmonitor_all_instances(regions, dry_run=True):
    """Stop detailed monitoring on all EC2 instances

    This will stop CloudWatch detailed monitoring on all instances 
    in all the regions in the input

    The dry_run parameter is now optional and it defaults to True.

    :param regions: List of AWS region names
    :param dry_run: If True, don't actually stop monitoring the instances (default is True)
    """

    print("====== EC2 - Unmonitor ======")

    # Create an EC2 resource object instead of a client object

    ec2 = boto3.resource('ec2')

    for region in regions:
        instances_to_unmonitor = []
        print(f'[INFO]: Getting instances in region: {region}')
        
        # Get all instances in the region using the EC2 resource object
        instances = ec2.instances.filter(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
        
        for instance in instances:
            instance_id = instance.instance_id
            monitor_state = instance.monitoring['State']
            
            if monitor_state == 'enabled':
                print(f'[INFO]: Instance with ID "{instance_id}" will be unmonitored.')
                instances_to_unmonitor.append(instance_id)

        if instances_to_unmonitor:
            if not dry_run:
                # Use the EC2 resource object to unmonitor the instances
                ec2.instances.filter(InstanceIds=instances_to_unmonitor).monitoring(False)
            print(f'[INFO]: Unmonitored instances: {str(instances_to_unmonitor)}')


# Delete EIP's

import boto3

def unmonitor_all_instances(regions, dry_run=True):
    """Stop detailed monitoring on all EC2 instances

    This will stop CloudWatch detailed monitoring on all instances 
    in all the regions in the input

    The dry_run parameter is now optional and it defaults to True.

    :param regions: List of AWS region names
    :param dry_run: If True, don't actually stop monitoring the instances (default is True)
    """

    print("====== EC2 - Unmonitor ======")

    # Create an EC2 resource object instead of a client object
    ec2 = boto3.resource('ec2')

    for region in regions:
        instances_to_unmonitor = []
        print(f'[INFO]: Getting instances in region: {region}')
        
        # Get all instances in the region using the EC2 resource object
        instances = ec2.instances.filter(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
        
        for instance in instances:
            instance_id = instance.instance_id
            monitor_state = instance.monitoring['State']
            
            if monitor_state == 'enabled':
                print(f'[INFO]: Instance with ID "{instance_id}" will be unmonitored.')
                instances_to_unmonitor.append(instance_id)

        if instances_to_unmonitor:
            if not dry_run:
                # Use the EC2 resource object to unmonitor the instances
                ec2.instances.filter(InstanceIds=instances_to_unmonitor).monitoring(False)
            print(f'[INFO]: Unmonitored instances: {str(instances_to_unmonitor)}')


# Delete EBS volumes

def delete_available_ebs_volumes(regions, dry_run=True):
    """
    Delete all available EBS (unassociated) volumes in all the regions in the input.
    :param regions: List of AWS region names.
    :param dry_run: If False, deletes the EBS volumes. By default, it's True.
    """
    deleted_resources = []
    check_resources = []
    skip_delete_resources = []

    for region in regions:
        print(f'[INFO]: Getting all available (unused) EBS volumes in region: {region}')
        ec2 = boto3.client('ec2', region_name=region)
        eks = boto3.client('eks', region_name=region)

        response = ec2.describe_volumes()

        for volume in response['Volumes']:
            if volume['State'] == 'available':
                volume_id = volume['VolumeId']
                delete_volume = True

                # Check if the volume is connected to a running EKS cluster.
                tags = volume.get('Tags', [])
                for tag in tags:
                    if tag['Key'].startswith('kubernetes.io/cluster'):
                        eks_cluster_name = tag['Key'].split('/')[2]
                        try:
                            eks_cluster = eks.describe_cluster(name=eks_cluster_name)
                            delete_volume = False  # Don't delete volume is it's connected to existing EKS cluster.
                        except eks.exceptions.ResourceNotFoundException:
                            delete_volume = True
                        break

                if delete_volume:
                    print(f'[INFO]: Deleting EBS volume with ID: {volume_id}')
                    if dry_run:
                        skip_delete_resources.append(('ec2', volume_id))
                    else:
                        try:
                            ec2.delete_volume(VolumeId=volume_id)
                            deleted_resources.append(('ec2', volume_id))
                        except Exception as e:
                            print(f'[ERROR]: Failed to delete volume with ID: {volume_id}. Error: {e}')
                            check_resources.append(('ec2', volume_id))

    # Prints out the results.
    print(f"[INFO]: Resources removed: {len(deleted_resources)} (total: {len(deleted_resources) + len(check_resources) + len(skip_delete_resources)})")
    if check_resources:
        print(f"[ERROR]: Some resources could not be deleted (total: {len(check_resources)}).")
    if skip_delete_resources:
        print(f"[INFO]: Resource deletion was skipped (total: {len(skip_delete_resources)}).")
    print("\n".join(f"[{resource_type}]: {resource_id}" for resource_type, resource_id in deleted_resources))



# Delete empty load balancers

import boto3

def delete_empty_load_balancers(regions, dry_run=False):
    """
    Delete all empty (classic) load balancers. This will delete all empty
    (with no instances) classic load balancers in all the regions in the input

    :param regions: List of AWS region names
    :param dry_run: If set to true, a dry run is done and no actual deletion occurs. Default is False
    :return:
        deleted_resources: List of tuples of deleted resources in the format (resource_type, resource_name)
        skipped_resources: List of tuples of skipped resources in the format (resource_type, resource_name)
        failed_resources: List of tuples of failed resources in the format (resource_type, resource_name, error_message)
    """
    deleted_resources = []
    skipped_resources = []
    failed_resources = []

    for region in regions:
        elb = boto3.client('elb', region_name=region)
        lbs = elb.describe_load_balancers()

        for lb in lbs['LoadBalancerDescriptions']:
            if len(lb['Instances']) == 0:
                lb_name = lb['LoadBalancerName']
                try:
                    if dry_run:
                        skipped_resources.append(('elb', lb_name))
                        print(f'[INFO]: Dry run: Skipped deleting classic load balancer: {lb_name}')
                    else:
                        elb.delete_load_balancer(LoadBalancerName=lb_name)
                        deleted_resources.append(('elb', lb_name))
                        print(f'[INFO]: Deleted classic load balancer: {lb_name}')
                except Exception as e:
                    error_message = f'Failed to delete classic load balancer: {lb_name}. Error: {e}'
                    failed_resources.append(('elb', lb_name, error_message))
                    print(f'[ERROR]: {error_message}')

    return deleted_resources, skipped_resources, failed_resources


# Stop RDS instances

import boto3
from concurrent.futures import ThreadPoolExecutor

def stop_rds(regions):
    """Stops RDS clusters and instances

    This will stop all RDS clusters and instances in all the regions in the input

    :param regions: List of AWS region names
    """

    print("====== RDS Clusters/Instances ======")
  
    def stop_rds_in_region(region):
        print(f'[INFO]: Getting RDS clusters and instances in region: {region}')
        rds_specific_region = boto3.client('rds', region_name=region)
        response = rds_specific_region.describe_db_clusters()
        for cluster in response['DBClusters']:
            if cluster['Status'] == 'available':
                cluster_id = cluster['DBClusterIdentifier']
                try:
                    print(f'[INFO]: Stopping DB cluster: {cluster_id}')
                    if dry_run == 'false':
                        response = rds_specific_region.stop_db_cluster(DBClusterIdentifier=cluster_id)
                except Exception as e:
                    print(f'[ERROR]: Failed to stop DB cluster: {cluster_id}. Error: {e}')

        response = rds_specific_region.describe_db_instances()
        for instance in response['DBInstances']:
            if instance['DBInstanceStatus'] == 'available':
                instance_id = instance['DBInstanceIdentifier']
                try:
                    print(f'[INFO]: Stopping DB instance: {instance_id}')
                    if dry_run == 'false':
                        response = rds_specific_region.stop_db_instance(DBInstanceIdentifier=instance_id)
                except Exception as e:
                    print(f'[ERROR]: Failed to stop DB instance: {instance_id}. Error: {e}')
                
    with ThreadPoolExecutor(max_workers=5) as executor:
        for region in regions:
            executor.submit(stop_rds_in_region, region)



# Delete EKS nodegroups

import boto3
import logging
from concurrent.futures import ThreadPoolExecutor

logging.basicConfig(level=logging.INFO)

def scale_in_eks_nodegroups(regions, dry_run=True):
    """Scales-in EKS nodegroups to 0

    This will ensure all EKS node groups have 0 replicas in all the regions in the input

    :param regions: List of AWS region names
    :param dry_run: Boolean flag that indicates whether the operation should be performed as a dry run
    """

    def scale_in_eks_nodegroups_in_region(region):
        logger = logging.getLogger(f'{__name__}.{region}')

        logger.info(f'Getting EKS clusters in region {region}')
        eks_specific_region = boto3.client('eks', region_name=region)
        response_clusters = eks_specific_region.list_clusters()

        for cluster in response_clusters['clusters']:
            response_nodegroups = eks_specific_region.list_nodegroups(clusterName=cluster)
            for ng in response_nodegroups['nodegroups']:
                node_group_info = eks_specific_region.describe_nodegroup(
                    clusterName=cluster, nodegroupName=ng)
                scaling_config = node_group_info['nodegroup']['scalingConfig']

                # Update scaling
                scaling_config['minSize'] = 0
                scaling_config['desiredSize'] = 0

                logger.info(f'Updating scaling config for node group {ng} in cluster {cluster}')
                if not dry_run:
                    try:
                        response = eks_specific_region.update_nodegroup_config(
                            clusterName=cluster, nodegroupName=ng,
                            scalingConfig=scaling_config)
                    except Exception as e:
                        logger.error(f'Failed to update scaling config for node group {ng} in cluster {cluster}. Error: {e}')

    with ThreadPoolExecutor(max_workers=5) as executor:
        for region in regions:
            executor.submit(scale_in_eks_nodegroups_in_region, region)


# Delete Kinesis Streams
def delete_kinesis_stream(regions):
    """Delete Kinesis stream

    :param regions: List of AWS region names
    """

    print("====== Kinesis Streams ======")
    for region in regions:
        print(
            f'[INFO]: Getting all Kinesis streams in the region: {region}')
        kinesis_client = boto3.client(
            'kinesis', region_name='{}'.format(region))
        response = kinesis_client.list_streams()

        for streamName in response['StreamNames']:
            try:
                if streamName.startswith("upsolver_"):
                    print(f'[INFO]: Skipped deleting Stream: {streamName}')
                    notify_resources.append(("kinesis", streamName))
                else:
                    if dry_run == 'false':
                        print(f'[INFO]: Deleting Stream: {streamName}')
                        del_response = kinesis_client.delete_stream(  # debug # check if deletion by version is req
                            StreamName=streamName,
                            EnforceConsumerDeletion=True
                        )
                        print(f"response from stream deletion: {del_response}")
                        log_deleted_resources(del_response, "kinesis", streamName)
                    else:
                        skip_delete_resources.append(("kinesis", streamName))
            except Exception as e:
                print(
                    f'[ERROR]: Failed to delete kinesis stream: {streamName}. Error: {e}')
                check_resources.append(("kinesis",streamName))


# Delete MSK streams

import boto3
from concurrent.futures import ThreadPoolExecutor

def delete_kinesis_stream(regions):
    """Delete Kinesis stream

    :param regions: List of AWS region names
    """

    print("====== Kinesis Streams ======")

    def delete_kinesis_stream_in_region(region):
        print(f'[INFO]: Getting all Kinesis streams in the region: {region}')
        kinesis_client = boto3.client('kinesis', region_name=region)
        response = kinesis_client.list_streams()

        for streamName in response['StreamNames']:
            try:
                if streamName.startswith("upsolver_"):
                    print(f'[INFO]: Skipped deleting Stream: {streamName}')
                    notify_resources.append(("kinesis", streamName))
                else:
                    if dry_run == 'false':
                        print(f'[INFO]: Deleting Stream: {streamName}')
                        del_response = kinesis_client.delete_stream(StreamName=streamName, EnforceConsumerDeletion=True)
                        print(f"response from stream deletion: {del_response}")
                        log_deleted_resources(del_response, "kinesis", streamName)
                    else:
                        skip_delete_resources.append(("kinesis", streamName))
            except Exception as e:
                print(f'[ERROR]: Failed to delete kinesis stream: {streamName}. Error: {e}')
                check_resources.append(("kinesis",streamName))

    with ThreadPoolExecutor(max_workers=5) as executor:
        for region in regions:
            executor.submit(delete_kinesis_stream_in_region, region)



# Delete OpenSearch  domains

import boto3
from concurrent.futures import ThreadPoolExecutor

def delete_domain(regions):
    """Delete OpenSearch domains

    :param regions: List of AWS region names
    """

    print("====== OpenSearch domains ======")

    def delete_domain_in_region(region):
        print(f'[INFO]: Getting all OpenSearch domains in the region: {region}')
        domain_client = boto3.client('opensearch', region_name=region)
        response = domain_client.list_domain_names(EngineType='OpenSearch')

        for domain_name in response['DomainNames']:
            try:
                if dry_run == 'false':
                    print(f'[INFO]: Deleting OpenSearch domains: {domain_name}')
                    delete_response = domain_client.delete_domain(DomainName=domain_name['DomainName'])
                    print(f"response from domain deletion: {delete_response}")
                    log_deleted_resources(delete_response, "opensearch", domain_name['DomainName'])
                else:
                    skip_delete_resources.append(("opensearch", domain_name['DomainName']))
            except Exception as e:
                print(f'[ERROR]: Failed to delete OpenSearch domains: {domain_name}. Error: {e}')
                check_resources.append(("opensearch", domain_name['DomainName']))

    with ThreadPoolExecutor(max_workers=5) as executor:
        for region in regions:
            executor.submit(delete_domain_in_region, region)

# Delete CreatedOn tag

import boto3
from concurrent.futures import ThreadPoolExecutor

def add_created_on_tag(regions):
    """Add "CreatedOn" tag on resources

    This will check the resource creation date against AWS Config
    and add it as a tag to the resource

    :param regions: List of AWS region names
    """

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
        response = config_specific_region.get_resource_config_history(
            resourceType='AWS::EC2::Instance',
            resourceId=instance_id)
        created_on = response['configurationItems'][0]['resourceCreationTime']
        created_on = created_on.strftime("%d/%m/%Y")
        print(f'[INFO] Instance {instance_id} created on {created_on}')

        # Create tag on instance
        if dry_run == 'false':
            ec2_specific_region.create_tags(
                Resources=[instance_id],
                Tags=[
                    {
                        'Key': 'CreatedOn',
                        'Value': created_on
                    },
                ]
            )

    with ThreadPoolExecutor(max_workers=5) as executor:
        for region in regions:
            print(f'[INFO]: Getting instances in region: {region}')
            ec2_specific_region = boto3.client('ec2', region_name=region)
            config_specific_region = boto3.client('config', region_name=region)

            # Check if there are discover resources in AWS Config
            response = config_specific_region.get_discovered_resource_counts()
            if response['totalDiscoveredResources'] == 0:
                continue

            response = ec2_specific_region.describe_instances()
            if "Reservations" in response:
                for reservation in response["Reservations"]:
                    if "Instances" in reservation:
                        instances = reservation["Instances"]
                        executor.map(process_instance, instances,
                                     [ec2_specific_region]*len(instances),
                                     [config_specific_region]*len(instances))

def lambda_handler(event, context):
    check_all_regions = os.environ['CHECK_ALL_REGIONS'] == 'true'
    if check_all_regions:
        regions = get_aws_regions()
    else:
        regions = USED_REGIONS

    stop_instances(regions)
    tag_instances(regions)
    unmonitor_instances(regions)
    release_unassociated_eip(regions)
    delete_ebs_volumes(regions)
    delete_empty_load_balancers(regions)
    stop_rds_instances(regions)
    scale_in_eks_nodegroups(regions)
    delete_kinesis_stream(regions)
    delete_msk_clusters(regions)
    delete_domain(regions)
    notify_auto_clean_data()

    return {
        'statusCode': 200,
        'body': json.dumps('Success!')
    }