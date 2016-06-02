import boto3


def get_instances(elb='site'):
    client = boto3.client('elb')

    site = client.describe_load_balancers(LoadBalancerNames=[elb])

    instances = [i['InstanceId'] for i in site['LoadBalancerDescriptions'][0]['Instances']]

    return instances

def get_instance_ip(instance_id):
    ec2 = boto3.resource('ec2')
    instance = ec2.Instance(instance_id)

    return instance.private_ip_address
