import boto3


def get_instances(elb, region_name):
    client = boto3.client('elb', region_name=region_name)

    site = client.describe_load_balancers(LoadBalancerNames=[elb])

    instances = [i['InstanceId'] for i in site['LoadBalancerDescriptions'][0]['Instances']]

    return instances


def get_instance_ip(instance_id, region_name):
    ec2 = boto3.resource('ec2', region_name=region_name)
    instance = ec2.Instance(instance_id)

    return instance.private_ip_address
